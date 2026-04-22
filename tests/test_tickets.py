import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.db.session import Base, get_db

# ── Test database (in-memory SQLite) ──────────────────────────────────────────
TEST_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


client = TestClient(app)

TICKET_PAYLOAD = {
    "title": "Network switch failure on floor 3",
    "description": "The network switch at rack B-12 is unresponsive since 07:30.",
    "requester_name": "John Smith",
    "requester_email": "john.smith@company.com",
    "priority": "high",
    "category": "network",
}


# ── Create ─────────────────────────────────────────────────────────────────────

def test_create_ticket():
    response = client.post("/api/v1/tickets/", json=TICKET_PAYLOAD)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == TICKET_PAYLOAD["title"]
    assert data["status"] == "open"
    assert data["priority"] == "high"


# ── List ───────────────────────────────────────────────────────────────────────

def test_list_tickets():
    client.post("/api/v1/tickets/", json=TICKET_PAYLOAD)
    response = client.get("/api/v1/tickets/")
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_list_tickets_filter_by_status():
    client.post("/api/v1/tickets/", json=TICKET_PAYLOAD)
    response = client.get("/api/v1/tickets/?status=open")
    assert response.status_code == 200
    assert all(t["status"] == "open" for t in response.json())


# ── Get ────────────────────────────────────────────────────────────────────────

def test_get_ticket():
    created = client.post("/api/v1/tickets/", json=TICKET_PAYLOAD).json()
    response = client.get(f"/api/v1/tickets/{created['id']}")
    assert response.status_code == 200
    assert response.json()["id"] == created["id"]


def test_get_ticket_not_found():
    response = client.get("/api/v1/tickets/9999")
    assert response.status_code == 404


# ── Update ─────────────────────────────────────────────────────────────────────

def test_update_ticket_status():
    created = client.post("/api/v1/tickets/", json=TICKET_PAYLOAD).json()
    response = client.patch(
        f"/api/v1/tickets/{created['id']}",
        json={"status": "in_progress", "assigned_to": "Tech Bob"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "in_progress"
    assert data["assigned_to"] == "Tech Bob"


def test_resolve_ticket_sets_resolved_at():
    created = client.post("/api/v1/tickets/", json=TICKET_PAYLOAD).json()
    response = client.patch(
        f"/api/v1/tickets/{created['id']}",
        json={"status": "resolved"},
    )
    assert response.status_code == 200
    assert response.json()["resolved_at"] is not None


# ── Delete ─────────────────────────────────────────────────────────────────────

def test_delete_ticket():
    created = client.post("/api/v1/tickets/", json=TICKET_PAYLOAD).json()
    response = client.delete(f"/api/v1/tickets/{created['id']}")
    assert response.status_code == 204
    assert client.get(f"/api/v1/tickets/{created['id']}").status_code == 404


# ── Interactions ───────────────────────────────────────────────────────────────

def test_add_interaction():
    created = client.post("/api/v1/tickets/", json=TICKET_PAYLOAD).json()
    response = client.post(
        f"/api/v1/tickets/{created['id']}/interactions",
        json={"author": "Tech Bob", "message": "We are on site, investigating.", "is_internal": False},
    )
    assert response.status_code == 201
    assert response.json()["author"] == "Tech Bob"


def test_list_interactions():
    created = client.post("/api/v1/tickets/", json=TICKET_PAYLOAD).json()
    client.post(
        f"/api/v1/tickets/{created['id']}/interactions",
        json={"author": "Tech Bob", "message": "Issue identified.", "is_internal": True},
    )
    response = client.get(f"/api/v1/tickets/{created['id']}/interactions")
    assert response.status_code == 200
    assert len(response.json()) == 1


# ── Stats ──────────────────────────────────────────────────────────────────────

def test_stats():
    client.post("/api/v1/tickets/", json=TICKET_PAYLOAD)
    response = client.get("/api/v1/tickets/stats")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["open"] == 1


# ── Health ─────────────────────────────────────────────────────────────────────

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
