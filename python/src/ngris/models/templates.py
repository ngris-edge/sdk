from __future__ import annotations

from datetime import datetime

from ngris.models._common import NgrisModel


class CustomTemplate(NgrisModel):
    uuid: str | None = None
    user_uuid: str | None = None
    # Deprecated: the integer ids below are removed from API responses at the
    # integer-id sunset (https://ngris.com/docs/public-ids). Use the *uuid fields.
    id: int | None = None
    user_id: int | None = None
    type: str
    content: str
    is_active: bool
    created_at: datetime


__all__ = ["CustomTemplate"]
