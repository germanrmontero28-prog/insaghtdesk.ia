"""Herramientas de solo lectura que el agente puede invocar.

Todas consultan SQLite a través de SQLAlchemy (consultas parametrizadas por
ORM) y nunca ejecutan SQL arbitrario ni modifican registros.
"""

from google.genai import types
from sqlalchemy.orm import Session

from app import crud, models

RESUMEN_DECLARATION = types.FunctionDeclaration(
    name="consultar_resumen_ventas",
    description=(
        "Obtiene el resumen global de ventas: ingresos totales, cantidad "
        "vendida, ticket promedio y el desglose de ingresos y cantidad por "
        "categoría. No admite parámetros."
    ),
    parameters=types.Schema(type=types.Type.OBJECT, properties={}),
)

VENTAS_POR_PRODUCTO_DECLARATION = types.FunctionDeclaration(
    name="consultar_ventas_por_producto",
    description=(
        "Obtiene las ventas acumuladas (número de ventas, cantidad e "
        "ingresos) de uno o varios productos. Filtra por producto_id exacto "
        "o por una coincidencia parcial del nombre."
    ),
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "producto_id": types.Schema(
                type=types.Type.INTEGER,
                description="Id exacto del producto a consultar.",
            ),
            "nombre": types.Schema(
                type=types.Type.STRING,
                description="Nombre o parte del nombre del producto a buscar.",
            ),
        },
    ),
)

VENTAS_POR_CATEGORIA_DECLARATION = types.FunctionDeclaration(
    name="consultar_ventas_por_categoria",
    description=(
        "Obtiene las ventas acumuladas (ingresos y cantidad) por categoría "
        "de producto. Si se indica 'categoria', filtra solo esa; si se "
        "omite, devuelve todas las categorías con ventas registradas."
    ),
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "categoria": types.Schema(
                type=types.Type.STRING,
                description="Nombre de la categoría a consultar.",
            ),
        },
    ),
)

AGENT_TOOLS = types.Tool(
    function_declarations=[
        RESUMEN_DECLARATION,
        VENTAS_POR_PRODUCTO_DECLARATION,
        VENTAS_POR_CATEGORIA_DECLARATION,
    ]
)


def consultar_resumen_ventas(db: Session) -> dict:
    return crud.calcular_indicadores(db)


def consultar_ventas_por_producto(
    db: Session, producto_id: int | None = None, nombre: str | None = None
) -> dict:
    query = db.query(models.Producto)
    if producto_id is not None:
        query = query.filter(models.Producto.id == producto_id)
    elif nombre:
        query = query.filter(models.Producto.nombre.ilike(f"%{nombre}%"))
    else:
        return {"error": "Debes indicar producto_id o nombre."}

    productos = query.all()
    if not productos:
        return {"error": "No se encontró ningún producto con ese criterio."}

    resultados = []
    for producto in productos:
        ventas = (
            db.query(models.Venta)
            .filter(models.Venta.producto_id == producto.id)
            .all()
        )
        cantidad = sum(v.cantidad for v in ventas)
        ingresos = sum(v.cantidad * v.precio_unitario for v in ventas)
        resultados.append(
            {
                "producto_id": producto.id,
                "nombre": producto.nombre,
                "categoria": producto.categoria,
                "numero_ventas": len(ventas),
                "cantidad_vendida": cantidad,
                "ingresos": float(ingresos),
            }
        )
    return {"productos": resultados}


def consultar_ventas_por_categoria(db: Session, categoria: str | None = None) -> dict:
    indicadores = crud.calcular_indicadores(db)
    categorias = indicadores["ventas_por_categoria"]
    if categoria:
        categorias = [
            c for c in categorias if c["categoria"].lower() == categoria.lower()
        ]
        if not categorias:
            return {
                "error": f"No hay ventas registradas para la categoría '{categoria}'."
            }
    return {"ventas_por_categoria": categorias}


TOOL_FUNCTIONS = {
    "consultar_resumen_ventas": consultar_resumen_ventas,
    "consultar_ventas_por_producto": consultar_ventas_por_producto,
    "consultar_ventas_por_categoria": consultar_ventas_por_categoria,
}
