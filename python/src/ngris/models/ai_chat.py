from __future__ import annotations

from datetime import datetime
from typing import Optional

from ngris.models._common import NgrisModel


class ChatSession(NgrisModel):
    id: int
    user_id: int
    title: Optional[str] = None
    created_at: datetime


class ChatMessage(NgrisModel):
    id: int
    session_id: int
    role: str
    content: str
    created_at: datetime


__all__ = ["ChatSession", "ChatMessage"]
