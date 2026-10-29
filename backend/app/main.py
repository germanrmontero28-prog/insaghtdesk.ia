from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app import crud, schemas
from app.agent import service as agent_service
from app.agent.client import get_gemini_client
from app.database import Base, engine, get_db
from app.seed import seed_database

load_dotenv(Path(__file__).resolve().parent.parent / ".env")


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    seed_database()
    yield


app = FastAPI(title="InsightDesk AI", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/productos", response_model=list[schemas.ProductoOut])
def get_productos(db: Session = Depends(get_db)):
    return crud.listar_productos(db)


@app.post("/api/productos", response_model=schemas.ProductoOut, status_code=201)
def post_producto(producto: schemas.ProductoCreate, db: Session = Depends(get_db)):
    return crud.crear_producto(db, producto)


@app.get("/api/ventas", response_model=list[schemas.VentaOut])
def get_ventas(db: Session = Depends(get_db)):
    return crud.listar_ventas(db)


@app.post("/api/ventas", response_model=schemas.VentaOut, status_code=201)
def post_venta(venta: schemas.VentaCreate, db: Session = Depends(get_db)):
    if crud.obtener_producto(db, venta.producto_id) is None:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return crud.crear_venta(db, venta)


@app.get("/api/indicadores", response_model=schemas.Indicadores)
def get_indicadores(db: Session = Depends(get_db)):
    return crud.calcular_indicadores(db)


@app.post("/api/agente/chat", response_model=schemas.AgentChatResponse)
def post_agente_chat(
    payload: schemas.AgentChatRequest,
    db: Session = Depends(get_db),
    client=Depends(get_gemini_client),
):
    try:
        return agent_service.responder_chat(db=db, client=client, mensaje=payload.mensaje)
    except agent_service.AgentError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc
