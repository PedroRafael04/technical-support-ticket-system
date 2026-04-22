from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.db.session import Base, engine
from app.api.v1.router import api_router

# Import models so SQLAlchemy registers them before creating tables
import app.models.ticket  # noqa: F401

# ── Create database tables ─────────────────────────────────────────────────────
Base.metadata.create_all(bind=engine)

# ── Application factory ────────────────────────────────────────────────────────
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""
## Technical Support Ticket System API

A backend system to manage technical support tickets in industrial environments.

### Features
- 🎫 **Ticket Management** — Create, update, prioritise, and close support tickets
- 🔄 **Status Workflow** — Track tickets through `open → in_progress → pending → resolved → closed`
- 💬 **Interaction History** — Log public replies and internal technician notes per ticket
- 📊 **Statistics** — Get a real-time overview of all ticket counts by status and priority
- 🔍 **Filtering** — Query tickets by status, priority, category, or assigned technician

### Priority Levels
| Level | Description |
|-------|-------------|
| `low` | No immediate impact |
| `medium` | Moderate impact, can wait |
| `high` | Significant impact on operations |
| `critical` | System down, immediate action required |
""",
    contact={
        "name": "GitHub Repository",
        "url": "https://github.com/yourusername/support-ticket-system",
    },
    license_info={
        "name": "MIT",
    },
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── CORS ───────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ────────────────────────────────────────────────────────────────────
app.include_router(api_router)


# ── Health check ───────────────────────────────────────────────────────────────
@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok", "app": settings.APP_NAME, "version": settings.APP_VERSION}
