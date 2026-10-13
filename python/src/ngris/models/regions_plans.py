from __future__ import annotations

from typing import Optional

from ngris.models._common import NgrisModel


class Region(NgrisModel):
    slug: str
    name: str
    display_name: str
    tunnel_server_address: str
    is_active: bool
    health_status: Optional[str] = None


class Plan(NgrisModel):
    # Plans are addressed by their slug (they have no uuid).
    slug: str
    id: Optional[int] = None  # deprecated: use slug
    name: str
    price_monthly: float
    price_yearly: float
    description: Optional[str] = None
    max_endpoints: int
    max_tunnels: int
    max_connections: int
    max_bandwidth: int
    allowed_protocols: Optional[str] = None
    allowed_regions: Optional[str] = None
    billing_model: Optional[str] = None
    is_purchasable: bool


class Addon(NgrisModel):
    id: Optional[int] = None  # deprecated: add-ons are addressed by ``key``
    key: str
    name: str
    description: Optional[str] = None
    enabled: bool
    unit_amount_cents: int
    currency: str
    interval: Optional[str] = None


__all__ = ["Region", "Plan", "Addon"]
