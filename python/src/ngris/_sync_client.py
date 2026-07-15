from __future__ import annotations

from typing import Any

from ngris._base_client import SyncBaseClient
from ngris._config import NgrisConfig
from ngris._version import __version__


class Ngris(SyncBaseClient):
    """Synchronous Ngris API client.

    Usage:
        client = Ngris(api_key="ngris_...")
        endpoints = client.endpoints.list()
        client.close()

    Or as a context manager:
        with Ngris(api_key="ngris_...") as client:
            for ep in client.endpoints.list_all():
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
        # Empty strings trigger NgrisConfig's env-var fallback (NGRIS_API_KEY,
        # NGRIS_BASE_URL). Passing `api_key=None` and not setting the env
        # var raises a clear AuthenticationError on first request rather
        # than a confusing 401 from the server.
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
        from ngris.services.auth import AuthService

        return self._services.setdefault("auth", AuthService(self))

    @property
    def users(self) -> Any:
        from ngris.services.users import UsersService

        return self._services.setdefault("users", UsersService(self))

    @property
    def billing(self) -> Any:
        from ngris.services.billing import BillingService

        return self._services.setdefault("billing", BillingService(self))

    @property
    def endpoints(self) -> Any:
        from ngris.services.endpoints import EndpointsService

        return self._services.setdefault("endpoints", EndpointsService(self))

    @property
    def endpoint_oauth(self) -> Any:
        from ngris.services.endpoint_oauth import EndpointOAuthService

        return self._services.setdefault("endpoint_oauth", EndpointOAuthService(self))

    @property
    def endpoint_rbac(self) -> Any:
        from ngris.services.endpoint_rbac import EndpointRBACService

        return self._services.setdefault("endpoint_rbac", EndpointRBACService(self))

    @property
    def traffic_policies(self) -> Any:
        from ngris.services.traffic_policies import TrafficPoliciesService

        return self._services.setdefault("traffic_policies", TrafficPoliciesService(self))

    @property
    def routing_rules(self) -> Any:
        from ngris.services.routing_rules import RoutingRulesService

        return self._services.setdefault("routing_rules", RoutingRulesService(self))

    @property
    def firewall(self) -> Any:
        from ngris.services.firewall import FirewallService

        return self._services.setdefault("firewall", FirewallService(self))

    @property
    def domains(self) -> Any:
        from ngris.services.domains import DomainsService

        return self._services.setdefault("domains", DomainsService(self))

    @property
    def certificates(self) -> Any:
        from ngris.services.certificates import CertificatesService

        return self._services.setdefault("certificates", CertificatesService(self))

    @property
    def api_keys(self) -> Any:
        from ngris.services.api_keys import APIKeysService

        return self._services.setdefault("api_keys", APIKeysService(self))

    @property
    def client_cas(self) -> Any:
        from ngris.services.client_cas import ClientCAsService

        return self._services.setdefault("client_cas", ClientCAsService(self))

    @property
    def tunnels(self) -> Any:
        from ngris.services.tunnels import TunnelsService

        return self._services.setdefault("tunnels", TunnelsService(self))

    @property
    def traffic(self) -> Any:
        from ngris.services.traffic import TrafficService

        return self._services.setdefault("traffic", TrafficService(self))

    @property
    def organizations(self) -> Any:
        from ngris.services.organizations import OrganizationsService

        return self._services.setdefault("organizations", OrganizationsService(self))

    @property
    def sso(self) -> Any:
        from ngris.services.sso import SSOService

        return self._services.setdefault("sso", SSOService(self))

    @property
    def dedicated_ips(self) -> Any:
        from ngris.services.dedicated_ips import DedicatedIPsService

        return self._services.setdefault("dedicated_ips", DedicatedIPsService(self))

    @property
    def ai_chat(self) -> Any:
        from ngris.services.ai_chat import AIChatService

        return self._services.setdefault("ai_chat", AIChatService(self))

    @property
    def support(self) -> Any:
        from ngris.services.support import SupportService

        return self._services.setdefault("support", SupportService(self))

    @property
    def templates(self) -> Any:
        from ngris.services.templates import TemplatesService

        return self._services.setdefault("templates", TemplatesService(self))

    @property
    def regions(self) -> Any:
        from ngris.services.regions_plans import RegionsPlansService

        return self._services.setdefault("regions", RegionsPlansService(self))
