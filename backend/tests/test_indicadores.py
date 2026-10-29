import pytest

from app.seed import NUM_VENTAS


def test_seed_genera_el_numero_de_ventas_esperado(client):
    ventas = client.get("/api/ventas").json()
    assert len(ventas) == NUM_VENTAS


def test_indicadores_consistentes_con_ventas(client):
    ventas = client.get("/api/ventas").json()
    indicadores = client.get("/api/indicadores").json()

    ingresos_esperados = sum(v["cantidad"] * v["precio_unitario"] for v in ventas)
    cantidad_esperada = sum(v["cantidad"] for v in ventas)

    assert indicadores["ingresos_totales"] == pytest.approx(ingresos_esperados)
    assert indicadores["cantidad_vendida"] == cantidad_esperada
    assert indicadores["ticket_promedio"] == pytest.approx(
        ingresos_esperados / cantidad_esperada
    )


def test_ventas_por_categoria_suman_el_total(client):
    indicadores = client.get("/api/indicadores").json()

    suma_ingresos_categorias = sum(
        c["ingresos"] for c in indicadores["ventas_por_categoria"]
    )
    suma_cantidad_categorias = sum(
        c["cantidad"] for c in indicadores["ventas_por_categoria"]
    )

    assert suma_ingresos_categorias == pytest.approx(indicadores["ingresos_totales"])
    assert suma_cantidad_categorias == indicadores["cantidad_vendida"]


def test_indicadores_sin_ventas_no_falla():
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy.pool import StaticPool

    from app import crud
    from app.database import Base

    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SessionLocal = sessionmaker(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        indicadores = crud.calcular_indicadores(db)
    finally:
        db.close()

    assert indicadores["ingresos_totales"] == 0
    assert indicadores["cantidad_vendida"] == 0
    assert indicadores["ticket_promedio"] == 0
    assert indicadores["ventas_por_categoria"] == []
