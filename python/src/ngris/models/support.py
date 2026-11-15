from __future__ import annotations

from datetime import datetime
from typing import Optional

from ngris.models._common import NgrisModel


class SupportTicket(NgrisModel):
    id: int
    uuid: str
    subject: str
    category: Optional[str] = None
    priority: str
    status: str
    created_at: datetime
    updated_at: datetime


class SupportTicketMessage(NgrisModel):
    """One message of a ticket's conversation, as the ticket API answers it."""

    id: int
    ticket_id: int
    content: str
    sender_type: str
    created_at: datetime


__all__ = ["SupportTicket", "SupportTicketMessage"]
