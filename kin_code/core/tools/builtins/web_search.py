"""Web search tool using Brave Search API."""

from __future__ import annotations

from collections.abc import AsyncGenerator
from http import HTTPStatus
import os
from typing import ClassVar

import httpx
from pydantic import BaseModel, Field

from kin_code.core.tools.base import (
    BaseTool,
    BaseToolConfig,
    BaseToolState,
    InvokeContext,
    ToolError,
    ToolPermission,
)
from kin_code.core.tools.ui import ToolCallDisplay, ToolResultDisplay, ToolUIData
from kin_code.core.types import ToolCallEvent, ToolResultEvent, ToolStreamEvent

BRAVE_API_KEY_ENV = "BRAVE_API_KEY"
BRAVE_SEARCH_URL = "https://api.search.brave.com/res/v1/web/search"


class WebSearchConfig(BaseToolConfig):
    """Configuration for the web search tool."""

    permission: ToolPermission = ToolPermission.ALWAYS
    default_count: int = Field(default=10, ge=1, le=20, description="Default number of results")
    timeout: int = Field(default=30, description="Request timeout in seconds")


class WebSearchArgs(BaseModel):
    """Arguments for web search."""

    query: str = Field(description="Search query. Use specific, targeted queries.")
    count: int | None = Field(
        default=None,
        ge=1,
        le=20,
        description="Number of results (1-20). Defaults to 10.",
    )


class SearchResultItem(BaseModel):
    """A single search result."""

    title: str
    url: str
    description: str


class WebSearchResult(BaseModel):
    """Result from web search."""

    query: str
    results: list[SearchResultItem]
    total_count: int


class WebSearch(
    BaseTool[WebSearchArgs, WebSearchResult, WebSearchConfig, BaseToolState],
    ToolUIData[WebSearchArgs, WebSearchResult],
):
    """Search the web using Brave Search API."""

    description: ClassVar[str] = """Search the web for current information.

USE WHEN:
- You need up-to-date information beyond your knowledge cutoff
- Researching technologies, libraries, or APIs
- Finding documentation or official sources
- Answering questions about recent events

DO NOT USE WHEN:
- The answer is already in your knowledge base
- You need to read a specific URL (use web_fetch instead)
- The query is about local files or codebase (use grep/read_file)

EXAMPLES:
- "Python 3.12 new features" - Find latest Python features
- "React 19 release date" - Check release information
- "httpx async client documentation" - Find library docs"""

    @classmethod
    def get_call_display(cls, event: ToolCallEvent) -> ToolCallDisplay:
        if not isinstance(event.args, WebSearchArgs):
            return ToolCallDisplay(summary="web_search")
        return ToolCallDisplay(summary=f"Searching: {event.args.query}")

    @classmethod
    def get_result_display(cls, event: ToolResultEvent) -> ToolResultDisplay:
        if not isinstance(event.result, WebSearchResult):
            return ToolResultDisplay(
                success=False, message=event.error or event.skip_reason or "No result"
            )
        return ToolResultDisplay(
            success=True,
            message=f"Found {event.result.total_count} results for '{event.result.query}'",
        )

    @classmethod
    def get_status_text(cls) -> str:
        return "Searching the web"

    async def run(
        self, args: WebSearchArgs, ctx: InvokeContext | None = None
    ) -> AsyncGenerator[ToolStreamEvent | WebSearchResult, None]:
        api_key = os.environ.get(BRAVE_API_KEY_ENV)
        if not api_key:
            raise ToolError(
                f"Brave Search API key not configured. "
                f"Set the {BRAVE_API_KEY_ENV} environment variable. "
                f"Get a key at: https://brave.com/search/api/"
            )

        if not args.query.strip():
            raise ToolError("Search query cannot be empty")

        count = args.count or self.config.default_count

        async with httpx.AsyncClient(timeout=self.config.timeout) as client:
            try:
                response = await client.get(
                    BRAVE_SEARCH_URL,
                    headers={
                        "Accept": "application/json",
                        "X-Subscription-Token": api_key,
                    },
                    params={
                        "q": args.query,
                        "count": count,
                    },
                )

                if response.status_code == HTTPStatus.UNAUTHORIZED:
                    raise ToolError("Invalid Brave Search API key")
                if response.status_code == HTTPStatus.TOO_MANY_REQUESTS:
                    raise ToolError("Brave Search rate limit exceeded. Try again later.")
                if response.status_code != HTTPStatus.OK:
                    raise ToolError(f"Brave Search API error: HTTP {response.status_code}")

                data = response.json()

            except httpx.TimeoutException:
                raise ToolError(f"Search request timed out after {self.config.timeout}s")
            except httpx.RequestError as e:
                raise ToolError(f"Search request failed: {e}") from e

        results = self._parse_results(data)

        yield WebSearchResult(
            query=args.query,
            results=results,
            total_count=len(results),
        )

    def _parse_results(self, data: dict) -> list[SearchResultItem]:
        """Parse Brave Search API response into SearchResultItems."""
        results: list[SearchResultItem] = []

        web_results = data.get("web", {}).get("results", [])
        for item in web_results:
            title = item.get("title", "")
            url = item.get("url", "")
            description = item.get("description", "")

            if title and url:
                results.append(
                    SearchResultItem(
                        title=title,
                        url=url,
                        description=description,
                    )
                )

        return results
