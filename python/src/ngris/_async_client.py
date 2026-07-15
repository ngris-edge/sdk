from __future__ import annotations

from typing import Any

from ngris._base_client import AsyncBaseClient
from ngris._config import NgrisConfig
from ngris._version import __version__


class AsyncNgris(AsyncBaseClient):
    """Asynchronous Ngris API client.

    Usage:
        client = AsyncNgris(api_key="ngris_...")
        endpoints = await client.endpoints.list()
        await client.close()

    Or as an async context manager:
        async with AsyncNgris(api_key="ngris_...") as client:
            async for ep in client.endpoints.list_all():
                print(ep.uuid, ep.public_url)
    """

    def __init__(
        self,
        api_key: str | None = None,
        *,
        base_url: str | None = None,
        timeout: float = 30.0,
        max_retries: int = 3,
        http2: bool = True,
        **kwargs: Any,
    ) -> None:
        # Same env-var-fallback contract as the sync client.
        config = NgrisConfig(
            base_url=base_url or "",
            api_key=api_key or "",
            timeout=timeout,
            max_retries=max_retries,
            http2=http2,
            **{k: v for k, v in kwargs.items() if k in NgrisConfig.__dataclass_fields__},
        )
        if not config.api_key:
            raise ValueError(
                "api_key is required. Pass api_key=... or set NGRIS_API_KEY env var."
            )
        super().__init__(config)
        self._services: dict[str, Any] = {}

    @property
    def auth(self) -> Any:
        from ngris.services.auth import AsyncAuthService

        return self._services.setdefault("auth", AsyncAuthService(self))

    @property
    def users(self) -> Any:
        from ngris.services.users import AsyncUsersService

        return self._services.setdefault("users", AsyncUsersService(self))

    @property
    def billing(self) -> Any:
        from ngris.services.billing import AsyncBillingService

        return self._services.setdefault("billing", AsyncBillingService(self))

    @property
    def endpoints(self) -> Any:
        from ngris.services.endpoints import AsyncEndpointsService

        return self._services.setdefault("endpoints", AsyncEndpointsService(self))

    @property
    def endpoint_oauth(self) -> Any:
        from ngris.services.endpoint_oauth import AsyncEndpointOAuthService

        return self._services.setdefault("endpoint_oauth", AsyncEndpointOAuthService(self))

    @property
    def endpoint_rbac(self) -> Any:
        from ngris.services.endpoint_rbac import AsyncEndpointRBACService

        return self._services.setdefault("endpoint_rbac", AsyncEndpointRBACService(self))

    @property
    def traffic_policies(self) -> Any:
        from ngris.services.traffic_policies import AsyncTrafficPoliciesService

        return self._services.setdefault("traffic_policies", AsyncTrafficPoliciesService(self))

    @property
    def routing_rules(self) -> Any:
        from ngris.services.routing_rules import AsyncRoutingRulesService

        return self._services.setdefault("routing_rules", AsyncRoutingRulesService(self))

    @property
    def firewall(self) -> Any:
        from ngris.services.firewall import AsyncFirewallService

        return self._services.setdefault("firewall", AsyncFirewallService(self))

    @property
    def domains(self) -> Any:
        from ngris.services.domains import AsyncDomainsService

        return self._services.setdefault("domains", AsyncDomainsService(self))

    @property
    def certificates(self) -> Any:
        from ngris.services.certificates import AsyncCertificatesService

        return self._services.setdefault("certificates", AsyncCertificatesService(self))

    @property
    def api_keys(self) -> Any:
        from ngris.services.api_keys import AsyncAPIKeysService

        return self._services.setdefault("api_keys", AsyncAPIKeysService(self))

    @property
    def client_cas(self) -> Any:
        from ngris.services.client_cas import AsyncClientCAsService

        return self._services.setdefault("client_cas", AsyncClientCAsService(self))

    @property
    def tunnels(self) -> Any:
        from ngris.services.tunnels import AsyncTunnelsService

        return self._services.setdefault("tunnels", AsyncTunnelsService(self))

    @property
    def traffic(self) -> Any:
        from ngris.services.traffic import AsyncTrafficService

        return self._services.setdefault("traffic", AsyncTrafficService(self))

    @property
    def organizations(self) -> Any:
        from ngris.services.organizations import AsyncOrganizationsService

        return self._services.setdefault("organizations", AsyncOrganizationsService(self))

    @property
    def sso(self) -> Any:
        from ngris.services.sso import AsyncSSOService

        return self._services.setdefault("sso", AsyncSSOService(self))

    @property
    def dedicated_ips(self) -> Any:
        from ngris.services.dedicated_ips import AsyncDedicatedIPsService

        return self._services.setdefault("dedicated_ips", AsyncDedicatedIPsService(self))

    @property
    def ai_chat(self) -> Any:
        from ngris.services.ai_chat import AsyncAIChatService

        return self._services.setdefault("ai_chat", AsyncAIChatService(self))

    @property
    def support(self) -> Any:
        from ngris.services.support import AsyncSupportService

        return self._services.setdefault("support", AsyncSupportService(self))

    @property
    def templates(self) -> Any:
        from ngris.services.templates import AsyncTemplatesService

        return self._services.setdefault("templates", AsyncTemplatesService(self))

    @property
    def regions(self) -> Any:
        from ngris.services.regions_plans import AsyncRegionsPlansService

        return self._services.setdefault("regions", AsyncRegionsPlansService(self))
