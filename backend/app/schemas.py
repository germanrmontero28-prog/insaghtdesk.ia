from datetime import date

from pydantic import BaseModel, ConfigDict, Field


class ProductoBase(BaseModel):
    nombre: str = Field(min_length=1)
    categoria: str = Field(min_length=1)
    precio: float = Field(gt=0)


class ProductoCreate(ProductoBase):
    pass


class ProductoOut(ProductoBase):
    model_config = ConfigDict(from_attributes=True)

    id: int


class VentaBase(BaseModel):
    producto_id: int
    cantidad: int = Field(gt=0)
    precio_unitario: float = Field(gt=0)
    fecha: date


class VentaCreate(VentaBase):
    pass


class VentaOut(VentaBase):
    model_config = ConfigDict(from_attributes=True)

    id: int


class VentaPorCategoria(BaseModel):
    categoria: str
    ingresos: float
    cantidad: int


class Indicadores(BaseModel):
    ingresos_totales: float
    cantidad_vendida: int
    ticket_promedio: float
    ventas_por_categoria: list[VentaPorCategoria]


class AgentChatRequest(BaseModel):
    mensaje: str = Field(min_length=1, max_length=2000)


class AgentChatResponse(BaseModel):
    respuesta: str
    herramientas: list[str] = Field(default_factory=list)
