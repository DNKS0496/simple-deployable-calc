from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app


AUTH_HEADERS = {"X-API-Key": "dev-api-key"}

@pytest.fixture()
def client(tmp_path: Path):
    test_db_path = tmp_path / "test_calculator.db"
    test_database_url = f"sqlite:///{test_db_path}"

    engine = create_engine(
        test_database_url,
        connect_args={"check_same_thread": False},
    )

    TestingSessionLocal = sessionmaker(
        bind=engine,
        autocommit=False,
        autoflush=False,
    )

    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)


def test_health_endpoint(client: TestClient):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_create_calculation(client: TestClient):
    response = client.post(
        "/calculations",
        json={
            "a": 10,
            "b": 5,
            "operation": "add",
        },
        headers=AUTH_HEADERS,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == 1
    assert data["a"] == 10
    assert data["b"] == 5
    assert data["operation"] == "add"
    assert data["result"] == 15


def test_list_calculations(client: TestClient):
    client.post(
        "/calculations",
        json={
            "a": 10,
            "b": 5,
            "operation": "add",
        },
        headers=AUTH_HEADERS,
    )

    response = client.get("/calculations", headers=AUTH_HEADERS,)

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["operation"] == "add"
    assert data[0]["result"] == 15


def test_get_calculation_by_id(client: TestClient):
    create_response = client.post(
        "/calculations",
        json={
            "a": 20,
            "b": 4,
            "operation": "divide",
        },
        headers=AUTH_HEADERS,
    )

    calculation_id = create_response.json()["id"]

    response = client.get(f"/calculations/{calculation_id}", headers=AUTH_HEADERS,)

    assert response.status_code == 200
    assert response.json()["result"] == 5


def test_get_missing_calculation_returns_404(client: TestClient):
    response = client.get("/calculations/999", headers=AUTH_HEADERS,)

    assert response.status_code == 404
    assert response.json()["detail"] == "Calculation not found"


def test_division_by_zero_returns_400(client: TestClient):
    response = client.post(
        "/calculations",
        json={
            "a": 10,
            "b": 0,
            "operation": "divide",
        },
        headers=AUTH_HEADERS,
    )

    assert response.status_code == 400
    assert "Division by zero" in response.json()["detail"]


def test_delete_calculation(client: TestClient):
    create_response = client.post(
        "/calculations",
        json={
            "a": 10,
            "b": 5,
            "operation": "add",
        },
        headers=AUTH_HEADERS,
    )

    calculation_id = create_response.json()["id"]

    delete_response = client.delete(f"/calculations/{calculation_id}", headers=AUTH_HEADERS,)

    assert delete_response.status_code == 200

    get_response = client.get(f"/calculations/{calculation_id}", headers=AUTH_HEADERS,)

    assert get_response.status_code == 404

def test_calculations_requires_api_key(client: TestClient):
    response = client.get("/calculations")

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid or missing API key"


def test_calculations_rejects_wrong_api_key(client: TestClient):
    response = client.get(
        "/calculations",
        headers={"X-API-Key": "wrong-key"},
    )

    assert response.status_code == 401