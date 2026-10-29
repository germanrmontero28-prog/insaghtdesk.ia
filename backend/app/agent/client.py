import os

from fastapi import HTTPException
from google import genai
from google.genai import types

REQUEST_TIMEOUT_MS = 30_000


def get_gemini_client() -> genai.Client:
    """Dependencia de FastAPI: construye el cliente de Gemini por request.

    La API key nunca sale del backend ni se incluye en respuestas de error.
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=503, detail="El servicio de IA no está configurado."
        )
    return genai.Client(
        api_key=api_key,
        http_options=types.HttpOptions(timeout=REQUEST_TIMEOUT_MS),
    )
