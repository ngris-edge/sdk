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
    id: int
    ticket_id: int
    content: str
    sender_type: str
    is_internal_note: bool
    created_at: datetime


__all__ = ["SupportTicket", "SupportTicketMessage"]
