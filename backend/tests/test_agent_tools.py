from app import crud, models
from app.agent import tools


def test_consultar_resumen_ventas_usa_datos_reales(db_session):
    resumen = tools.consultar_resumen_ventas(db_session)
    esperado = crud.calcular_indicadores(db_session)

    assert resumen == esperado
    assert resumen["cantidad_vendida"] > 0


def test_consultar_ventas_por_producto_por_id(db_session):
    producto = db_session.query(models.Producto).first()

    resultado = tools.consultar_ventas_por_producto(db_session, producto_id=producto.id)

    assert "productos" in resultado
    assert resultado["productos"][0]["producto_id"] == producto.id
    assert resultado["productos"][0]["nombre"] == producto.nombre


def test_consultar_ventas_por_producto_por_nombre_parcial(db_session):
    producto = db_session.query(models.Producto).first()
    fragmento = producto.nombre[:4]

    resultado = tools.consultar_ventas_por_producto(db_session, nombre=fragmento)

    nombres = [p["nombre"] for p in resultado["productos"]]
    assert producto.nombre in nombres


def test_consultar_ventas_por_producto_sin_criterio(db_session):
    resultado = tools.consultar_ventas_por_producto(db_session)

    assert "error" in resultado


def test_consultar_ventas_por_producto_inexistente(db_session):
    resultado = tools.consultar_ventas_por_producto(
        db_session, nombre="Producto Que No Existe"
    )

    assert "error" in resultado


def test_consultar_ventas_por_categoria_filtra(db_session):
    todas = tools.consultar_ventas_por_categoria(db_session)
    categoria_objetivo = todas["ventas_por_categoria"][0]["categoria"]

    filtrado = tools.consultar_ventas_por_categoria(db_session, categoria=categoria_objetivo)

    assert len(filtrado["ventas_por_categoria"]) == 1
    assert filtrado["ventas_por_categoria"][0]["categoria"] == categoria_objetivo


def test_consultar_ventas_por_categoria_inexistente(db_session):
    resultado = tools.consultar_ventas_por_categoria(
        db_session, categoria="Categoría Inexistente"
    )

    assert "error" in resultado
