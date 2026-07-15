from __future__ import annotations

from ngris.models._common import NgrisModel


class OAuthProvider(NgrisModel):
    id: int
    endpoint_id: int
    provider_type: str
    provider_name: str
    client_id: str
    auth_url: str
    token_url: str
    user_info_url: str
    scopes: str
    identifier_field: str
    enabled: bool


class OAuthProviderPreset(NgrisModel):
    provider_type: str
    name: str
    default_scopes: str
    auth_url: str | None = None
    token_url: str | None = None
    user_info_url: str | None = None


__all__ = ["OAuthProvider", "OAuthProviderPreset"]
