from sqlalchemy import func
from sqlalchemy.orm import Session

from app import models, schemas


def crear_producto(db: Session, producto: schemas.ProductoCreate) -> models.Producto:
    db_producto = models.Producto(**producto.model_dump())
    db.add(db_producto)
    db.commit()
    db.refresh(db_producto)
    return db_producto


def listar_productos(db: Session) -> list[models.Producto]:
    return db.query(models.Producto).order_by(models.Producto.id).all()


def obtener_producto(db: Session, producto_id: int) -> models.Producto | None:
    return db.get(models.Producto, producto_id)


def crear_venta(db: Session, venta: schemas.VentaCreate) -> models.Venta:
    db_venta = models.Venta(**venta.model_dump())
    db.add(db_venta)
    db.commit()
    db.refresh(db_venta)
    return db_venta


def listar_ventas(db: Session) -> list[models.Venta]:
    return db.query(models.Venta).order_by(models.Venta.id).all()


def calcular_indicadores(db: Session) -> dict:
    importe_venta = models.Venta.cantidad * models.Venta.precio_unitario
    ingresos_totales, cantidad_vendida = db.query(
        func.coalesce(func.sum(importe_venta), 0.0),
        func.coalesce(func.sum(models.Venta.cantidad), 0),
    ).one()
    ticket_promedio = (ingresos_totales / cantidad_vendida) if cantidad_vendida else 0.0

    filas = (
        db.query(
            models.Producto.categoria,
            func.sum(importe_venta).label("ingresos"),
            func.sum(models.Venta.cantidad).label("cantidad"),
        )
        .join(models.Venta, models.Venta.producto_id == models.Producto.id)
        .group_by(models.Producto.categoria)
        .order_by(models.Producto.categoria)
        .all()
    )
    ventas_por_categoria = [
        {
            "categoria": fila.categoria,
            "ingresos": float(fila.ingresos or 0),
            "cantidad": int(fila.cantidad or 0),
        }
        for fila in filas
    ]

    return {
        "ingresos_totales": float(ingresos_totales or 0),
        "cantidad_vendida": int(cantidad_vendida or 0),
        "ticket_promedio": float(ticket_promedio),
        "ventas_por_categoria": ventas_por_categoria,
    }
