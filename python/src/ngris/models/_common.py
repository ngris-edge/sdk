from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class NgrisModel(BaseModel):
    """Base for all Ngris API models."""

    model_config = {"populate_by_name": True, "extra": "ignore"}
