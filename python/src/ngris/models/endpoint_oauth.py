from __future__ import annotations

from ngris.models._common import NgrisModel


class OAuthProvider(NgrisModel):
    uuid: str | None = None
    endpoint_uuid: str | None = None
    # Deprecated: the integer ids below are removed from API responses at the
    # integer-id sunset (https://ngris.com/docs/public-ids). Use the *uuid fields.
    id: int | None = None
    endpoint_id: int | None = None
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
