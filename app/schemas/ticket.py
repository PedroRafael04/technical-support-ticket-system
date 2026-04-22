from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field

from app.models.enums import TicketPriority, TicketStatus, TicketCategory


# ── Interaction schemas ────────────────────────────────────────────────────────

class InteractionCreate(BaseModel):
    author: str = Field(..., min_length=2, max_length=100, examples=["John Doe"])
    message: str = Field(..., min_length=1, examples=["We are investigating the issue."])
    is_internal: bool = Field(False, description="Mark as internal note (not visible to requester)")


class InteractionResponse(BaseModel):
    id: int
    ticket_id: int
    author: str
    message: str
    is_internal: bool
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Ticket schemas ─────────────────────────────────────────────────────────────

class TicketCreate(BaseModel):
    title: str = Field(..., min_length=5, max_length=255, examples=["Printer not responding on floor 2"])
    description: str = Field(..., min_length=10, examples=["The printer at station B2 is offline since 08:00."])
    requester_name: str = Field(..., min_length=2, max_length=100, examples=["Alice Silva"])
    requester_email: EmailStr = Field(..., examples=["alice.silva@company.com"])
    priority: TicketPriority = Field(TicketPriority.MEDIUM)
    category: TicketCategory = Field(TicketCategory.OTHER)


class TicketUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=5, max_length=255)
    description: Optional[str] = Field(None, min_length=10)
    assigned_to: Optional[str] = Field(None, max_length=100)
    priority: Optional[TicketPriority] = None
    status: Optional[TicketStatus] = None
    category: Optional[TicketCategory] = None


class TicketSummary(BaseModel):
    id: int
    title: str
    requester_name: str
    priority: TicketPriority
    status: TicketStatus
    category: TicketCategory
    assigned_to: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TicketResponse(TicketSummary):
    description: str
    requester_email: str
    resolved_at: Optional[datetime]
    interactions: list[InteractionResponse] = []

    model_config = {"from_attributes": True}


# ── Stats schema ───────────────────────────────────────────────────────────────

class TicketStats(BaseModel):
    total: int
    open: int
    in_progress: int
    pending: int
    resolved: int
    closed: int
    critical: int
    high: int
