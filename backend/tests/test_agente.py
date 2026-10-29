import pytest
from google.genai import errors, types

from app.agent.client import get_gemini_client
from app.main import app


def _respuesta_con_function_call(nombre: str, args: dict | None = None):
    return types.GenerateContentResponse(
        candidates=[
            types.Candidate(
                content=types.Content(
                    role="model",
                    parts=[types.Part.from_function_call(name=nombre, args=args or {})],
                )
            )
        ]
    )


def _respuesta_con_texto(texto: str):
    return types.GenerateContentResponse(
        candidates=[
            types.Candidate(
                content=types.Content(role="model", parts=[types.Part(text=texto)])
            )
        ]
    )


def _respuesta_vacia():
    return types.GenerateContentResponse(candidates=[])


class FakeModels:
    """Simula `client.models` devolviendo respuestas guionizadas en orden."""

    def __init__(self, respuestas):
        self._respuestas = list(respuestas)
        self.llamadas = []

    def generate_content(self, *, model, contents, config):
        self.llamadas.append({"model": model, "contents": contents, "config": config})
        siguiente = self._respuestas.pop(0)
        if isinstance(siguiente, Exception):
            raise siguiente
        return siguiente


class FakeGeminiClient:
    def __init__(self, respuestas):
        self.models = FakeModels(respuestas)


@pytest.fixture(autouse=True)
def _limpiar_override_gemini():
    yield
    app.dependency_overrides.pop(get_gemini_client, None)


def test_chat_usa_herramienta_y_responde(client):
    fake = FakeGeminiClient(
        [
            _respuesta_con_function_call("consultar_resumen_ventas"),
            _respuesta_con_texto(
                "Los ingresos totales son sólidos. Recomendación: reforzar Electrónica."
            ),
        ]
    )
    app.dependency_overrides[get_gemini_client] = lambda: fake

    response = client.post("/api/agente/chat", json={"mensaje": "¿Cómo van las ventas?"})

    assert response.status_code == 200
    body = response.json()
    assert "Recomendación" in body["respuesta"]
    assert body["herramientas"] == ["consultar_resumen_ventas"]
    assert len(fake.models.llamadas) == 2


def test_chat_consulta_ventas_por_categoria(client):
    fake = FakeGeminiClient(
        [
            _respuesta_con_function_call(
                "consultar_ventas_por_categoria", {"categoria": "Oficina"}
            ),
            _respuesta_con_texto("La categoría Oficina generó buenos ingresos."),
        ]
    )
    app.dependency_overrides[get_gemini_client] = lambda: fake

    response = client.post("/api/agente/chat", json={"mensaje": "¿Cómo va Oficina?"})

    assert response.status_code == 200
    assert response.json()["herramientas"] == ["consultar_ventas_por_categoria"]


def test_chat_encadena_varias_herramientas(client):
    fake = FakeGeminiClient(
        [
            _respuesta_con_function_call("consultar_resumen_ventas"),
            _respuesta_con_function_call(
                "consultar_ventas_por_producto", {"nombre": "Laptop"}
            ),
            _respuesta_con_texto("Comparativa lista."),
        ]
    )
    app.dependency_overrides[get_gemini_client] = lambda: fake

    response = client.post(
        "/api/agente/chat", json={"mensaje": "Compara el resumen con la laptop"}
    )

    assert response.status_code == 200
    assert response.json()["herramientas"] == [
        "consultar_resumen_ventas",
        "consultar_ventas_por_producto",
    ]
    assert len(fake.models.llamadas) == 3


def test_chat_error_autenticacion_no_expone_detalle(client):
    fake = FakeGeminiClient(
        [errors.ClientError(401, {"error": {"message": "invalid api key AIzaSyFAKE"}})]
    )
    app.dependency_overrides[get_gemini_client] = lambda: fake

    response = client.post("/api/agente/chat", json={"mensaje": "hola"})

    assert response.status_code == 503
    assert "AIzaSyFAKE" not in response.text
    assert "GEMINI_API_KEY" not in response.text


def test_chat_error_cuota(client):
    fake = FakeGeminiClient(
        [errors.ClientError(429, {"error": {"message": "quota exceeded"}})]
    )
    app.dependency_overrides[get_gemini_client] = lambda: fake

    response = client.post("/api/agente/chat", json={"mensaje": "hola"})

    assert response.status_code == 429


def test_chat_error_servidor(client):
    fake = FakeGeminiClient(
        [errors.ServerError(503, {"error": {"message": "unavailable"}})]
    )
    app.dependency_overrides[get_gemini_client] = lambda: fake

    response = client.post("/api/agente/chat", json={"mensaje": "hola"})

    assert response.status_code == 503


def test_chat_error_timeout(client):
    fake = FakeGeminiClient([TimeoutError("timed out")])
    app.dependency_overrides[get_gemini_client] = lambda: fake

    response = client.post("/api/agente/chat", json={"mensaje": "hola"})

    assert response.status_code == 504


def test_chat_respuesta_vacia(client):
    fake = FakeGeminiClient([_respuesta_vacia()])
    app.dependency_overrides[get_gemini_client] = lambda: fake

    response = client.post("/api/agente/chat", json={"mensaje": "hola"})

    assert response.status_code == 502


def test_chat_sin_texto_ni_function_call_es_respuesta_vacia(client):
    fake = FakeGeminiClient(
        [
            types.GenerateContentResponse(
                candidates=[
                    types.Candidate(content=types.Content(role="model", parts=[]))
                ]
            )
        ]
    )
    app.dependency_overrides[get_gemini_client] = lambda: fake

    response = client.post("/api/agente/chat", json={"mensaje": "hola"})

    assert response.status_code == 502


def test_chat_sin_api_key_configurada(client, monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

    response = client.post("/api/agente/chat", json={"mensaje": "hola"})

    assert response.status_code == 503


def test_chat_mensaje_vacio_rechazado(client):
    # La validación de Pydantic debe rechazar el mensaje vacío
    # independientemente de si el agente está configurado; se provee un
    # cliente falso para aislar esta prueba de esa dependencia.
    app.dependency_overrides[get_gemini_client] = lambda: FakeGeminiClient([])

    response = client.post("/api/agente/chat", json={"mensaje": ""})

    assert response.status_code == 422
