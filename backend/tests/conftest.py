import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app.main as main_module
from app.database import Base, get_db
from app.main import app
from app.seed import seed_database

TEST_DATABASE_URL = "sqlite://"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture()
def client(monkeypatch):
    Base.metadata.create_all(bind=engine)
    seed_database(session_factory=TestingSessionLocal)

    # Evita que el lifespan de la app toque el motor/BD de producción al
    # entrar al TestClient (que dispara los eventos de startup).
    monkeypatch.setattr(main_module, "engine", engine)
    monkeypatch.setattr(
        main_module, "seed_database", lambda: seed_database(session_factory=TestingSessionLocal)
    )
    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def db_session(client):
    """Sesión directa sobre la misma base en memoria que usa `client`."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
