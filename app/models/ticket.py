from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, Text, DateTime, Enum as SAEnum, ForeignKey
from sqlalchemy.orm import relationship

from app.db.session import Base
from app.models.enums import TicketPriority, TicketStatus, TicketCategory


class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    requester_name = Column(String(100), nullable=False)
    requester_email = Column(String(150), nullable=False)
    assigned_to = Column(String(100), nullable=True)
    priority = Column(SAEnum(TicketPriority), nullable=False, default=TicketPriority.MEDIUM)
    status = Column(SAEnum(TicketStatus), nullable=False, default=TicketStatus.OPEN)
    category = Column(SAEnum(TicketCategory), nullable=False, default=TicketCategory.OTHER)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc))
    resolved_at = Column(DateTime, nullable=True)

    interactions = relationship("Interaction", back_populates="ticket",
                                cascade="all, delete-orphan", order_by="Interaction.created_at")


class Interaction(Base):
    __tablename__ = "interactions"

    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(Integer, ForeignKey("tickets.id", ondelete="CASCADE"), nullable=False)
    author = Column(String(100), nullable=False)
    message = Column(Text, nullable=False)
    is_internal = Column(Integer, default=0)  # 0 = public, 1 = internal note
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    ticket = relationship("Ticket", back_populates="interactions")
