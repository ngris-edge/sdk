from __future__ import annotations

from typing import AsyncIterator, Generic, Iterator, TypeVar

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


# Hard cap applied to PageIterator / AsyncPageIterator. Protects against
# misbehaving servers (e.g., total=999_999, items=[1] per page → 1M
# round-trips) and against pagination bugs that fail to advance page_num.
# Configurable via NgrisConfig.max_pages and overridable per-iterator.
DEFAULT_MAX_PAGES = 1000


class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    # `total` is Optional because some endpoints don't include it, and
    # silently coercing missing values to 0 would short-circuit
    # has_more / iteration on the very first page.
    total: int | None = None
    page: int
    page_size: int

    @property
    def has_more(self) -> bool:
        # Unknown total → defer to "did we get a full page?" — caller
        # iteration should request page+1 and stop on empty response.
        if self.total is None:
            return len(self.items) >= self.page_size
        return self.page * self.page_size < self.total


class PageIterator(Generic[T]):
    """Iterates through all pages, yielding items one at a time.

    Stops on empty page OR when total is exceeded OR when max_pages is
    hit (defensive against runaway server responses).
    """

    def __init__(self, fetch_page, page_size: int = 50, max_pages: int = DEFAULT_MAX_PAGES) -> None:
        self._fetch_page = fetch_page
        self._page_size = page_size
        self._max_pages = max_pages
        self._current_page: list[T] = []
        self._index = 0
        self._page_num = 0
        self._total: int | None = None
        self._pages_fetched = 0

    def __iter__(self) -> Iterator[T]:
        return self

    def __next__(self) -> T:
        while True:
            if self._index < len(self._current_page):
                item = self._current_page[self._index]
                self._index += 1
                return item

            if self._total is not None and self._page_num * self._page_size >= self._total:
                raise StopIteration

            if self._pages_fetched >= self._max_pages:
                raise StopIteration

            resp = self._fetch_page(self._page_num + 1, self._page_size)
            # Defensive: if the server returns the same page number we
            # asked for (or a stale one), advance ourselves rather than
            # trusting the response. Otherwise a buggy server that always
            # returns page=0 would loop forever.
            self._page_num = max(self._page_num + 1, resp.page)
            self._current_page = resp.items
            self._total = resp.total
            self._index = 0
            self._pages_fetched += 1

            if not self._current_page:
                raise StopIteration


class AsyncPageIterator(Generic[T]):
    """Async version of PageIterator. Same semantics + safety caps."""

    def __init__(self, fetch_page, page_size: int = 50, max_pages: int = DEFAULT_MAX_PAGES) -> None:
        self._fetch_page = fetch_page
        self._page_size = page_size
        self._max_pages = max_pages
        self._current_page: list[T] = []
        self._index = 0
        self._page_num = 0
        self._total: int | None = None
        self._pages_fetched = 0

    def __aiter__(self) -> AsyncIterator[T]:
        return self

    async def __anext__(self) -> T:
        while True:
            if self._index < len(self._current_page):
                item = self._current_page[self._index]
                self._index += 1
                return item

            if self._total is not None and self._page_num * self._page_size >= self._total:
                raise StopAsyncIteration

            if self._pages_fetched >= self._max_pages:
                raise StopAsyncIteration

            resp = await self._fetch_page(self._page_num + 1, self._page_size)
            self._page_num = max(self._page_num + 1, resp.page)
            self._current_page = resp.items
            self._total = resp.total
            self._index = 0
            self._pages_fetched += 1

            if not self._current_page:
                raise StopAsyncIteration
