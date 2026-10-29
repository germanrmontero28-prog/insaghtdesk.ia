from app.seed import NUM_VENTAS


def test_listar_ventas_seed(client):
    response = client.get("/api/ventas")
    assert response.status_code == 200
    assert len(response.json()) == NUM_VENTAS


def test_crear_venta(client):
    producto_id = client.get("/api/productos").json()[0]["id"]
    payload = {
        "producto_id": producto_id,
        "cantidad": 3,
        "precio_unitario": 10.0,
        "fecha": "2026-05-01",
    }
    response = client.post("/api/ventas", json=payload)
    assert response.status_code == 201
    body = response.json()
    assert body["cantidad"] == 3

    ventas = client.get("/api/ventas").json()
    assert len(ventas) == NUM_VENTAS + 1


def test_crear_venta_producto_inexistente(client):
    payload = {
        "producto_id": 9999,
        "cantidad": 1,
        "precio_unitario": 10.0,
        "fecha": "2026-05-01",
    }
    response = client.post("/api/ventas", json=payload)
    assert response.status_code == 404


def test_crear_venta_cantidad_invalida(client):
    producto_id = client.get("/api/productos").json()[0]["id"]
    payload = {
        "producto_id": producto_id,
        "cantidad": 0,
        "precio_unitario": 10.0,
        "fecha": "2026-05-01",
    }
    response = client.post("/api/ventas", json=payload)
    assert response.status_code == 422


def test_crear_venta_fecha_invalida(client):
    producto_id = client.get("/api/productos").json()[0]["id"]
    payload = {
        "producto_id": producto_id,
        "cantidad": 1,
        "precio_unitario": 10.0,
        "fecha": "no-es-una-fecha",
    }
    response = client.post("/api/ventas", json=payload)
    assert response.status_code == 422
