import logging
import os

import httpx
from google.genai import errors, types
from sqlalchemy.orm import Session

from app.agent.tools import AGENT_TOOLS, TOOL_FUNCTIONS

logger = logging.getLogger(__name__)

DEFAULT_MODEL = "gemini-3.8-flash"
MAX_TOOL_ROUNDS = 4

SYSTEM_INSTRUCTION = (
    "Eres un analista comercial de InsightDesk AI. Respondes preguntas sobre "
    "ventas usando EXCLUSIVAMENTE los datos devueltos por las herramientas "
    "disponibles (consultar_resumen_ventas, consultar_ventas_por_producto, "
    "consultar_ventas_por_categoria). Nunca inventes cifras: si una "
    "herramienta no encuentra datos, dilo explícitamente. Cuando los datos "
    "lo permitan, cierra tu respuesta con una recomendación comercial breve "
    "y concreta basada en esos datos."
)


class AgentError(Exception):
    def __init__(self, message: str, status_code: int):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


def _mapear_error_gemini(exc: Exception) -> AgentError:
    if isinstance(exc, errors.ClientError):
        if exc.code in (401, 403):
            logger.warning("Error de autenticación con Gemini (code=%s).", exc.code)
            return AgentError("No se pudo autenticar con el servicio de IA.", 503)
        if exc.code == 429:
            logger.warning("Cuota de Gemini excedida (code=%s).", exc.code)
            return AgentError(
                "El servicio de IA alcanzó su límite de uso. Intenta de nuevo más tarde.",
                429,
            )
        logger.warning("Error del cliente al llamar a Gemini (code=%s).", exc.code)
        return AgentError("No se pudo procesar la consulta con el agente.", 502)
    if isinstance(exc, errors.ServerError):
        logger.warning("Error del servidor de Gemini (code=%s).", exc.code)
        if exc.code == 504:
            return AgentError("El agente tardó demasiado en responder.", 504)
        return AgentError("El servicio de IA no está disponible en este momento.", 503)
    if isinstance(exc, (TimeoutError, httpx.TimeoutException)):
        logger.warning("Timeout al llamar a Gemini.")
        return AgentError("El agente tardó demasiado en responder.", 504)
    logger.exception("Error inesperado al llamar a Gemini.")
    return AgentError("Ocurrió un error inesperado al consultar al agente.", 502)


def responder_chat(db: Session, client, mensaje: str) -> dict:
    model = os.environ.get("GEMINI_MODEL", DEFAULT_MODEL)
    contents: list[types.Content] = [
        types.Content(role="user", parts=[types.Part(text=mensaje)])
    ]
    herramientas_usadas: list[str] = []

    for _ in range(MAX_TOOL_ROUNDS):
        try:
            response = client.models.generate_content(
                model=model,
                contents=contents,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_INSTRUCTION,
                    tools=[AGENT_TOOLS],
                ),
            )
        except (errors.APIError, TimeoutError, httpx.TimeoutException) as exc:
            raise _mapear_error_gemini(exc) from exc

        if not response or not response.candidates or not response.candidates[0].content:
            raise AgentError("El agente no devolvió una respuesta.", 502)

        function_calls = response.function_calls
        if not function_calls:
            texto = response.text
            if not texto:
                raise AgentError("El agente devolvió una respuesta vacía.", 502)
            return {"respuesta": texto, "herramientas": herramientas_usadas}

        contents.append(response.candidates[0].content)

        response_parts = []
        for call in function_calls:
            nombre = call.name
            argumentos = dict(call.args or {})
            fn = TOOL_FUNCTIONS.get(nombre)
            if fn is None:
                resultado = {"error": f"Herramienta desconocida: {nombre}"}
            else:
                try:
                    resultado = fn(db, **argumentos)
                except Exception:
                    logger.exception("Error ejecutando la herramienta %s", nombre)
                    resultado = {"error": "No se pudo ejecutar la herramienta."}
            herramientas_usadas.append(nombre)
            response_parts.append(
                types.Part.from_function_response(name=nombre, response=resultado)
            )

        contents.append(types.Content(role="user", parts=response_parts))

    raise AgentError(
        "El agente no pudo completar la consulta tras varios intentos.", 502
    )
