from __future__ import annotations

from typing import Any

from ngris.models.billing import (
    Balance,
    CheckoutSession,
    Invoice,
    PaymentMethod,
    PortalSession,
    SubscriptionStatus,
)
from ngris.services._base import AsyncBaseService, BaseService


class BillingService(BaseService):
    """Sync billing service."""

    def checkout(
        self,
        plan_id: int,
        interval: str = "monthly",
        payment_method_id: str | None = None,
    ) -> CheckoutSession:
        body: dict[str, Any] = {"plan_id": plan_id, "interval": interval}
        if payment_method_id is not None:
            body["payment_method_id"] = payment_method_id
        return self._client._post_json("/billing/checkout", body, CheckoutSession)

    def get_subscription(self) -> SubscriptionStatus:
        return self._client._get_json("/billing/subscription", SubscriptionStatus)

    def cancel(self) -> None:
        self._client._post_void("/billing/cancel", {})

    def reactivate(self) -> None:
        self._client._post_void("/billing/reactivate", {})

    def pause(self) -> None:
        self._client._post_void("/billing/pause", {})

    def resume(self) -> None:
        self._client._post_void("/billing/resume", {})

    def portal(self) -> PortalSession:
        return self._client._post_json("/billing/portal", {}, PortalSession)

    def list_payment_methods(self) -> list[PaymentMethod]:
        resp = self._client._get("/billing/payment-methods")
        data = resp.json()
        return [PaymentMethod.model_validate(item) for item in data]

    def list_invoices(self) -> list[Invoice]:
        resp = self._client._get("/billing/invoices")
        data = resp.json()
        return [Invoice.model_validate(item) for item in data]

    def get_balance(self) -> Balance:
        return self._client._get_json("/billing/balance", Balance)

    def validate_coupon(self, code: str, plan: str | None = None) -> dict[str, Any]:
        body: dict[str, Any] = {"code": code}
        if plan is not None:
            body["plan"] = plan
        return self._client._post_raw("/coupons/validate", body)


class AsyncBillingService(AsyncBaseService):
    """Async billing service."""

    async def checkout(
        self,
        plan_id: int,
        interval: str = "monthly",
        payment_method_id: str | None = None,
    ) -> CheckoutSession:
        body: dict[str, Any] = {"plan_id": plan_id, "interval": interval}
        if payment_method_id is not None:
            body["payment_method_id"] = payment_method_id
        return await self._client._post_json("/billing/checkout", body, CheckoutSession)

    async def get_subscription(self) -> SubscriptionStatus:
        return await self._client._get_json("/billing/subscription", SubscriptionStatus)

    async def cancel(self) -> None:
        await self._client._post_void("/billing/cancel", {})

    async def reactivate(self) -> None:
        await self._client._post_void("/billing/reactivate", {})

    async def pause(self) -> None:
        await self._client._post_void("/billing/pause", {})

    async def resume(self) -> None:
        await self._client._post_void("/billing/resume", {})

    async def portal(self) -> PortalSession:
        return await self._client._post_json("/billing/portal", {}, PortalSession)

    async def list_payment_methods(self) -> list[PaymentMethod]:
        resp = await self._client._get("/billing/payment-methods")
        data = resp.json()
        return [PaymentMethod.model_validate(item) for item in data]

    async def list_invoices(self) -> list[Invoice]:
        resp = await self._client._get("/billing/invoices")
        data = resp.json()
        return [Invoice.model_validate(item) for item in data]

    async def get_balance(self) -> Balance:
        return await self._client._get_json("/billing/balance", Balance)

    async def validate_coupon(self, code: str, plan: str | None = None) -> dict[str, Any]:
        body: dict[str, Any] = {"code": code}
        if plan is not None:
            body["plan"] = plan
        return await self._client._post_raw("/coupons/validate", body)
