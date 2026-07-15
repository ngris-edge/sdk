from __future__ import annotations

from datetime import datetime

from ngris.models._common import NgrisModel


class CustomTemplate(NgrisModel):
    id: int
    user_id: int
    type: str
    content: str
    is_active: bool
    created_at: datetime


__all__ = ["CustomTemplate"]
