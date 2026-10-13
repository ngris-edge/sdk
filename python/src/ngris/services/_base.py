from __future__ import annotations

import warnings
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ngris._base_client import AsyncBaseClient, SyncBaseClient


# Public ids (ngris API, 2026-10): every object is addressed by its ``uuid``.
# Integer ids are deprecated and stop working at the API's integer-id sunset;
# until then the SDK still passes an integer through (with a
# DeprecationWarning) so existing code keeps running while it migrates.
PUBLIC_IDS_DOCS = "https://ngris.com/docs/public-ids"


def _is_legacy_int(value: object) -> bool:
    if isinstance(value, bool):
        return False
    if isinstance(value, int):
        return True
    return isinstance(value, str) and value.isascii() and value.isdigit()


# The warnings point at the SDK user's call: _warn_* -> helper -> service
# method -> caller is stacklevel 4; ``extra`` adds the frames of a body-building
# function between the helper and the service method.
def _warn_legacy(what: str, extra: int = 0) -> None:
    warnings.warn(
        f"{what}: integer ids are deprecated and stop working at the ngris API's "
        f"integer-id sunset; pass the resource's uuid instead (see {PUBLIC_IDS_DOCS})",
        DeprecationWarning,
        stacklevel=4 + extra,
    )


def _warn_renamed(old: str, new: str, extra: int = 0) -> None:
    warnings.warn(
        f"{old}= is deprecated; use {new}= (see {PUBLIC_IDS_DOCS})",
        DeprecationWarning,
        stacklevel=4 + extra,
    )


def path_id(value: str | int, name: str) -> str:
    """Return the path segment for a resource id: the resource's uuid.

    A legacy integer id is passed through unchanged (it keeps working until
    the API's integer-id sunset) with a DeprecationWarning.
    """
    if _is_legacy_int(value):
        _warn_legacy(name)
    return str(value)


def put_ref(body: dict[str, Any], base: str, value: str | int | None, *, _extra: int = 0) -> None:
    """Set a reference to another object on a request body.

    A uuid is sent as ``<base>_uuid``. A legacy integer id is sent under the
    deprecated ``<base>_id`` name (accepted until the API's integer-id
    sunset) with a DeprecationWarning. ``None`` sets nothing.
    """
    if value is None:
        return
    if _is_legacy_int(value):
        _warn_legacy(f"{base}_id", _extra)
        body[f"{base}_id"] = int(value)
        return
    body[f"{base}_uuid"] = str(value)


def renamed_kwarg(new_value: Any, old_value: Any, old: str, new: str, *, _extra: int = 0) -> Any:
    """Resolve a keyword argument that was renamed (``old`` -> ``new``).

    Passing the old name still works, with a DeprecationWarning; passing both
    is an error.
    """
    if old_value is None:
        return new_value
    if new_value is not None:
        raise TypeError(f"pass {new}= only, not both {new}= and {old}=")
    _warn_renamed(old, new, _extra)
    return old_value


class BaseService:
    """Base class for sync service modules."""

    def __init__(self, client: SyncBaseClient) -> None:
        self._client = client


class AsyncBaseService:
    """Base class for async service modules."""

    def __init__(self, client: AsyncBaseClient) -> None:
        self._client = client
