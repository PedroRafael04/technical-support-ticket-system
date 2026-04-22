from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.ticket import Ticket, Interaction
from app.models.enums import TicketStatus
from app.schemas.ticket import TicketCreate, TicketUpdate, InteractionCreate, TicketStats


class TicketService:

    # ── Tickets ────────────────────────────────────────────────────────────────

    @staticmethod
    def create_ticket(db: Session, data: TicketCreate) -> Ticket:
        ticket = Ticket(**data.model_dump())
        db.add(ticket)
        db.commit()
        db.refresh(ticket)
        return ticket

    @staticmethod
    def get_ticket(db: Session, ticket_id: int) -> Optional[Ticket]:
        return db.query(Ticket).filter(Ticket.id == ticket_id).first()

    @staticmethod
    def list_tickets(
        db: Session,
        status: Optional[TicketStatus] = None,
        priority: Optional[str] = None,
        category: Optional[str] = None,
        assigned_to: Optional[str] = None,
        skip: int = 0,
        limit: int = 20,
    ) -> list[Ticket]:
        query = db.query(Ticket)
        if status:
            query = query.filter(Ticket.status == status)
        if priority:
            query = query.filter(Ticket.priority == priority)
        if category:
            query = query.filter(Ticket.category == category)
        if assigned_to:
            query = query.filter(Ticket.assigned_to == assigned_to)
        return query.order_by(Ticket.created_at.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def update_ticket(db: Session, ticket: Ticket, data: TicketUpdate) -> Ticket:
        updates = data.model_dump(exclude_unset=True)

        # Auto-set resolved_at when status changes to resolved
        if updates.get("status") == TicketStatus.RESOLVED and ticket.status != TicketStatus.RESOLVED:
            updates["resolved_at"] = datetime.now(timezone.utc)

        # Clear resolved_at if ticket is reopened
        if updates.get("status") == TicketStatus.OPEN:
            updates["resolved_at"] = None

        for field, value in updates.items():
            setattr(ticket, field, value)

        ticket.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(ticket)
        return ticket

    @staticmethod
    def delete_ticket(db: Session, ticket: Ticket) -> None:
        db.delete(ticket)
        db.commit()

    @staticmethod
    def get_stats(db: Session) -> TicketStats:
        from app.models.enums import TicketStatus, TicketPriority

        total = db.query(func.count(Ticket.id)).scalar()
        open_ = db.query(func.count(Ticket.id)).filter(Ticket.status == TicketStatus.OPEN).scalar()
        in_progress = db.query(func.count(Ticket.id)).filter(Ticket.status == TicketStatus.IN_PROGRESS).scalar()
        pending = db.query(func.count(Ticket.id)).filter(Ticket.status == TicketStatus.PENDING).scalar()
        resolved = db.query(func.count(Ticket.id)).filter(Ticket.status == TicketStatus.RESOLVED).scalar()
        closed = db.query(func.count(Ticket.id)).filter(Ticket.status == TicketStatus.CLOSED).scalar()
        critical = db.query(func.count(Ticket.id)).filter(Ticket.priority == TicketPriority.CRITICAL).scalar()
        high = db.query(func.count(Ticket.id)).filter(Ticket.priority == TicketPriority.HIGH).scalar()

        return TicketStats(
            total=total,
            open=open_,
            in_progress=in_progress,
            pending=pending,
            resolved=resolved,
            closed=closed,
            critical=critical,
            high=high,
        )

    # ── Interactions ───────────────────────────────────────────────────────────

    @staticmethod
    def add_interaction(db: Session, ticket: Ticket, data: InteractionCreate) -> Interaction:
        interaction = Interaction(
            ticket_id=ticket.id,
            author=data.author,
            message=data.message,
            is_internal=int(data.is_internal),
        )
        db.add(interaction)
        ticket.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(interaction)
        return interaction

    @staticmethod
    def list_interactions(db: Session, ticket_id: int) -> list[Interaction]:
        return (
            db.query(Interaction)
            .filter(Interaction.ticket_id == ticket_id)
            .order_by(Interaction.created_at.asc())
            .all()
        )
