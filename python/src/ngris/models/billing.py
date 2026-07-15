from __future__ import annotations

from datetime import datetime
from typing import Optional

from ngris.models._common import NgrisModel


class Subscription(NgrisModel):
    id: str | None = None
    status: str | None = None
    cancel_at_period_end: bool = False
    paused: bool = False
    interval: str | None = None
    current_period_end: int | None = None


class SubscriptionStatus(NgrisModel):
    plan: str
    plan_id: int | None = None
    has_subscription: bool = False
    subscription: Optional[Subscription] = None


class PaymentMethod(NgrisModel):
    id: str
    brand: str
    last4: str
    exp_month: int
    exp_year: int
    is_default: bool = False
    expiring: bool = False
    expired: bool = False


class Invoice(NgrisModel):
    id: str
    number: str | None = None
    amount_due: int
    amount_paid: int
    currency: str
    status: str
    created: int | None = None


class Balance(NgrisModel):
    balance_cents: int = 0
    currency: str = "usd"


class CheckoutSession(NgrisModel):
    url: str | None = None
    session_id: str | None = None


class PortalSession(NgrisModel):
    url: str | None = None


__all__ = [
    "Subscription",
    "SubscriptionStatus",
    "PaymentMethod",
    "Invoice",
    "Balance",
    "CheckoutSession",
    "PortalSession",
]
