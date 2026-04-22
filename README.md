# Technical Support Ticket System

A backend REST API built with **Python** and **FastAPI** to manage technical support tickets in industrial environments. Designed to simulate real-world support operations with structured workflows, priority management, status tracking, and full interaction history per ticket.

---

## Features

- **Ticket Management** — Create, update, prioritise, assign, and close support tickets
- **Status Workflow** — Structured lifecycle: `open → in_progress → pending → resolved → closed`
- **Priority Levels** — Four-tier system: `low`, `medium`, `high`, `critical`
- **Interaction History** — Log public replies and internal technician notes per ticket
- **Statistics Endpoint** — Real-time overview of ticket distribution by status and priority
- **Filtering & Pagination** — Query tickets by status, priority, category, or assigned technician
- **Auto-documentation** — Interactive Swagger UI available at `/docs`

---

## Tech Stack

| Layer | Technology |
|---|---|
| Framework | [FastAPI](https://fastapi.tiangolo.com/) |
| ORM | [SQLAlchemy 2.0](https://www.sqlalchemy.org/) |
| Validation | [Pydantic v2](https://docs.pydantic.dev/) |
| Database | SQLite (dev) — easily swappable to PostgreSQL |
| Server | [Uvicorn](https://www.uvicorn.org/) |
| Testing | [Pytest](https://pytest.org/) + FastAPI TestClient |

---

## Project Structure

```
support-ticket-system/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── endpoints/
│   │       │   └── tickets.py      # Route handlers
│   │       └── router.py           # API v1 router
│   ├── core/
│   │   └── config.py               # App settings (pydantic-settings)
│   ├── db/
│   │   └── session.py              # SQLAlchemy engine & session
│   ├── models/
│   │   ├── enums.py                # TicketStatus, TicketPriority, TicketCategory
│   │   └── ticket.py               # Ticket & Interaction ORM models
│   ├── schemas/
│   │   └── ticket.py               # Pydantic request/response schemas
│   ├── services/
│   │   └── ticket_service.py       # Business logic layer
│   └── main.py                     # FastAPI app factory & startup
├── tests/
│   └── test_tickets.py             # Pytest test suite
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

---

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/support-ticket-system.git
cd support-ticket-system
```

### 2. Create and activate a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate      # Linux / macOS
.venv\Scripts\activate         # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment

```bash
cp .env.example .env
```

### 5. Run the application

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`.

---

## API Documentation

After starting the server, access the interactive docs:

| Interface | URL |
|---|---|
| Swagger UI | [http://localhost:8000/docs](http://localhost:8000/docs) |
| ReDoc | [http://localhost:8000/redoc](http://localhost:8000/redoc) |
| Health Check | [http://localhost:8000/health](http://localhost:8000/health) |

---

## API Endpoints

### Tickets

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/v1/tickets/` | Create a new ticket |
| `GET` | `/api/v1/tickets/{id}` | Get ticket by ID |
| `GET` | `/api/v1/tickets/` | List all tickets (with filters) |
| `GET` | `/api/v1/tickets/stats` | Get ticket statistics |
| `PATCH` | `/api/v1/tickets/{id}` | Update a ticket |
| `DELETE` | `/api/v1/tickets/{id}` | Delete a ticket |

### Interactions

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/v1/tickets/{id}/interactions` | Add interaction to ticket |
| `GET` | `/api/v1/tickets/{id}/interactions` | List ticket interactions |

### Filtering (Query Parameters)

```
GET /api/v1/tickets/?status=open&priority=critical&category=network&assigned_to=Tech Bob
```

---

## Ticket Workflow

```
OPEN ──► IN_PROGRESS ──► PENDING ──► RESOLVED ──► CLOSED
  ▲                                      │
  └──────────────────────────────────────┘  (reopen clears resolved_at)
```

- Transitioning to `resolved` automatically sets `resolved_at`
- Reopening a ticket (back to `open`) clears `resolved_at`

---

## Running Tests

```bash
pytest tests/ -v
```

---

## Example Request

**Create a ticket:**

```bash
curl -X POST http://localhost:8000/api/v1/tickets/ \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Network switch failure on floor 3",
    "description": "The switch at rack B-12 has been unresponsive since 07:30.",
    "requester_name": "John Smith",
    "requester_email": "john.smith@company.com",
    "priority": "critical",
    "category": "network"
  }'
```

**Add an interaction:**

```bash
curl -X POST http://localhost:8000/api/v1/tickets/1/interactions \
  -H "Content-Type: application/json" \
  -d '{
    "author": "Tech Bob",
    "message": "On site — switch replaced, testing connectivity.",
    "is_internal": false
  }'
```

---