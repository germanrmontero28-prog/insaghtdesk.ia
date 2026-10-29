import random
from datetime import date, timedelta

from app.database import SessionLocal
from app import models

PRODUCTOS_DEMO = [
    {"nombre": "Laptop Pro 14", "categoria": "Electrónica", "precio": 1200.0},
    {"nombre": "Mouse Inalámbrico", "categoria": "Electrónica", "precio": 25.0},
    {"nombre": "Silla Ergonómica", "categoria": "Oficina", "precio": 180.0},
    {"nombre": "Escritorio Ajustable", "categoria": "Oficina", "precio": 350.0},
    {"nombre": "Cafetera Automática", "categoria": "Hogar", "precio": 90.0},
    {"nombre": "Set de Sábanas", "categoria": "Hogar", "precio": 45.0},
    {"nombre": "Zapatillas Running", "categoria": "Deporte", "precio": 75.0},
    {"nombre": "Mancuernas 10kg", "categoria": "Deporte", "precio": 60.0},
]

SEED = 42
NUM_VENTAS = 50
FECHA_INICIO = date(2026, 1, 1)
RANGO_DIAS = 270


def seed_database(session_factory=SessionLocal) -> None:
    db = session_factory()
    try:
        if db.query(models.Producto).count() > 0:
            return

        rng = random.Random(SEED)

        productos = [models.Producto(**data) for data in PRODUCTOS_DEMO]
        db.add_all(productos)
        db.commit()
        for producto in productos:
            db.refresh(producto)

        ventas = []
        for _ in range(NUM_VENTAS):
            producto = rng.choice(productos)
            cantidad = rng.randint(1, 5)
            fecha = FECHA_INICIO + timedelta(days=rng.randint(0, RANGO_DIAS))
            ventas.append(
                models.Venta(
                    producto_id=producto.id,
                    cantidad=cantidad,
                    precio_unitario=producto.precio,
                    fecha=fecha,
                )
            )
        db.add_all(ventas)
        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
