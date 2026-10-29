from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app import models
from app.database import Base
from app.seed import NUM_VENTAS, PRODUCTOS_DEMO, seed_database


def _nueva_sesion_vacia():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SessionLocal = sessionmaker(bind=engine)
    Base.metadata.create_all(bind=engine)
    return SessionLocal


def test_seed_genera_productos_y_ventas_esperados():
    SessionLocal = _nueva_sesion_vacia()
    seed_database(session_factory=SessionLocal)

    db = SessionLocal()
    try:
        assert db.query(models.Producto).count() == len(PRODUCTOS_DEMO)
        assert db.query(models.Venta).count() == NUM_VENTAS
    finally:
        db.close()


def test_seed_es_idempotente():
    SessionLocal = _nueva_sesion_vacia()
    seed_database(session_factory=SessionLocal)
    seed_database(session_factory=SessionLocal)

    db = SessionLocal()
    try:
        assert db.query(models.Producto).count() == len(PRODUCTOS_DEMO)
        assert db.query(models.Venta).count() == NUM_VENTAS
    finally:
        db.close()


def test_seed_es_reproducible_entre_bases_distintas():
    SessionLocal_a = _nueva_sesion_vacia()
    SessionLocal_b = _nueva_sesion_vacia()
    seed_database(session_factory=SessionLocal_a)
    seed_database(session_factory=SessionLocal_b)

    db_a = SessionLocal_a()
    db_b = SessionLocal_b()
    try:
        ventas_a = [
            (v.producto_id, v.cantidad, v.precio_unitario, v.fecha.isoformat())
            for v in db_a.query(models.Venta).order_by(models.Venta.id).all()
        ]
        ventas_b = [
            (v.producto_id, v.cantidad, v.precio_unitario, v.fecha.isoformat())
            for v in db_b.query(models.Venta).order_by(models.Venta.id).all()
        ]
        assert ventas_a == ventas_b
    finally:
        db_a.close()
        db_b.close()
