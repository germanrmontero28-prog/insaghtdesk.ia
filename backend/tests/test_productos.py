from app.seed import PRODUCTOS_DEMO


def test_listar_productos_devuelve_seed(client):
    response = client.get("/api/productos")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == len(PRODUCTOS_DEMO)
    assert data[0]["nombre"] == PRODUCTOS_DEMO[0]["nombre"]


def test_crear_producto(client):
    payload = {"nombre": "Teclado Mecánico", "categoria": "Electrónica", "precio": 55.0}
    response = client.post("/api/productos", json=payload)
    assert response.status_code == 201
    body = response.json()
    assert body["nombre"] == payload["nombre"]
    assert "id" in body

    listado = client.get("/api/productos").json()
    assert len(listado) == len(PRODUCTOS_DEMO) + 1


def test_crear_producto_precio_invalido(client):
    payload = {"nombre": "Producto X", "categoria": "Otros", "precio": -5}
    response = client.post("/api/productos", json=payload)
    assert response.status_code == 422


def test_crear_producto_nombre_vacio(client):
    payload = {"nombre": "", "categoria": "Otros", "precio": 10}
    response = client.post("/api/productos", json=payload)
    assert response.status_code == 422
