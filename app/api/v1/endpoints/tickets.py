from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.enums import TicketStatus, TicketPriority, TicketCategory
from app.schemas.ticket import (
    TicketCreate,
    TicketUpdate,
    TicketResponse,
    TicketSummary,
    TicketStats,
    InteractionCreate,
    InteractionResponse,
)
from app.services.ticket_service import TicketService

router = APIRouter(prefix="/tickets", tags=["Tickets"])


# ── Tickets ────────────────────────────────────────────────────────────────────

@router.post(
    "/",
    response_model=TicketResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new support ticket",
)
def create_ticket(payload: TicketCreate, db: Session = Depends(get_db)):
    """
    Opens a new technical support ticket with the given details.

    - **priority**: low | medium | high | critical
    - **category**: hardware | software | network | access | other
    """
    return TicketService.create_ticket(db, payload)


@router.get(
    "/",
    response_model=list[TicketSummary],
    summary="List all tickets",
)
def list_tickets(
    status: Optional[TicketStatus] = Query(None, description="Filter by status"),
    priority: Optional[TicketPriority] = Query(None, description="Filter by priority"),
    category: Optional[TicketCategory] = Query(None, description="Filter by category"),
    assigned_to: Optional[str] = Query(None, description="Filter by assigned technician"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """
    Returns a paginated list of tickets. Supports filtering by status, priority, category,
    and assigned technician.
    """
    return TicketService.list_tickets(db, status, priority, category, assigned_to, skip, limit)


@router.get(
    "/stats",
    response_model=TicketStats,
    summary="Get ticket statistics",
)
def get_stats(db: Session = Depends(get_db)):
    """Returns an overview of all ticket counts grouped by status and priority."""
    return TicketService.get_stats(db)


@router.get(
    "/{ticket_id}",
    response_model=TicketResponse,
    summary="Get a ticket by ID",
)
def get_ticket(ticket_id: int, db: Session = Depends(get_db)):
    """Retrieves a single ticket along with its full interaction history."""
    ticket = TicketService.get_ticket(db, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail=f"Ticket #{ticket_id} not found.")
    return ticket


@router.patch(
    "/{ticket_id}",
    response_model=TicketResponse,
    summary="Update a ticket",
)
def update_ticket(ticket_id: int, payload: TicketUpdate, db: Session = Depends(get_db)):
    """
    Partially updates a ticket. Only provided fields are changed.

    - Changing status to **resolved** automatically sets `resolved_at`.
    - Changing status back to **open** clears `resolved_at`.
    """
    ticket = TicketService.get_ticket(db, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail=f"Ticket #{ticket_id} not found.")
    return TicketService.update_ticket(db, ticket, payload)


@router.delete(
    "/{ticket_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a ticket",
)
def delete_ticket(ticket_id: int, db: Session = Depends(get_db)):
    """Permanently deletes a ticket and all its interactions."""
    ticket = TicketService.get_ticket(db, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail=f"Ticket #{ticket_id} not found.")
    TicketService.delete_ticket(db, ticket)


# ── Interactions ───────────────────────────────────────────────────────────────

@router.post(
    "/{ticket_id}/interactions",
    response_model=InteractionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add an interaction to a ticket",
)
def add_interaction(ticket_id: int, payload: InteractionCreate, db: Session = Depends(get_db)):
    """
    Appends a new message or internal note to a ticket's interaction history.

    - Set `is_internal: true` to mark the entry as an internal technician note.
    """
    ticket = TicketService.get_ticket(db, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail=f"Ticket #{ticket_id} not found.")
    return TicketService.add_interaction(db, ticket, payload)


@router.get(
    "/{ticket_id}/interactions",
    response_model=list[InteractionResponse],
    summary="List interactions of a ticket",
)
def list_interactions(ticket_id: int, db: Session = Depends(get_db)):
    """Returns all interactions for a given ticket, ordered chronologically."""
    ticket = TicketService.get_ticket(db, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail=f"Ticket #{ticket_id} not found.")
    return TicketService.list_interactions(db, ticket_id)
