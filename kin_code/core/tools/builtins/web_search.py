"""Web search tool using the Brave Search API.

This tool provides web search capabilities for the agent by querying the
Brave Search API. It returns lightweight metadata (title, URL, description)
to keep context manageable, rather than full page content.

Usage:
    The tool requires a BRAVE_SEARCH_API_KEY environment variable.
    Get a free API key at https://brave.com/search/api/

Example:
    result = await web_search.run(WebSearchArgs(query="Python async tutorial"))
    for item in result.results:
        print(f"{item.title}: {item.url}")
"""

from __future__ import annotations

import os
from typing import TYPE_CHECKING, Any, ClassVar, final

import httpx
from pydantic import BaseModel, Field

from kin_code.core.tools.base import (
    BaseTool,
    BaseToolConfig,
    BaseToolState,
    ToolError,
    ToolPermission,
)
from kin_code.core.tools.ui import ToolCallDisplay, ToolResultDisplay, ToolUIData
from kin_code.core.utils import async_retry

if TYPE_CHECKING:
    from kin_code.core.types import ToolCallEvent, ToolResultEvent


class WebSearchArgs(BaseModel):
    """Arguments for the web search tool."""

    query: str = Field(description="The search query")
    count: int = Field(
        default=10, ge=1, le=20, description="Number of results to return"
    )
    freshness: str | None = Field(
        default=None,
        description="Time filter: 'pd' (past day), 'pw' (past week), "
        "'pm' (past month), 'py' (past year)",
    )


class WebSearchResultItem(BaseModel):
    """A single search result item."""

    title: str
    url: str
    description: str


class WebSearchResult(BaseModel):
    """Result of a web search operation."""

    results: list[WebSearchResultItem]
    query: str
    total_count: int


class WebSearchToolConfig(BaseToolConfig):
    """Configuration for the web search tool."""

    permission: ToolPermission = ToolPermission.ASK
    api_key_env_var: str = Field(default="BRAVE_SEARCH_API_KEY")
    default_count: int = Field(default=10)
    max_snippet_length: int = Field(default=500)
    timeout: float = Field(default=30.0)
    safesearch: str = Field(default="moderate")


class WebSearchState(BaseToolState):
    """State for the web search tool."""

    recent_queries: list[str] = Field(default_factory=list)


def _is_retryable_search_error(e: Exception) -> bool:
    """Check if an exception is retryable for web search."""
    if isinstance(e, httpx.HTTPStatusError):
        return e.response.status_code in {408, 429, 500, 502, 503, 504}
    if isinstance(e, httpx.TimeoutException | httpx.ConnectError):
        return True
    return False


class WebSearch(
    BaseTool[WebSearchArgs, WebSearchResult, WebSearchToolConfig, WebSearchState],
    ToolUIData[WebSearchArgs, WebSearchResult],
):
    """Search the web using the Brave Search API.

    Returns lightweight metadata (title, URL, description) for search results.
    Use WebFetch to retrieve full page content from specific URLs.
    """

    description: ClassVar[str] = (
        "Search the web using the Brave Search API. "
        "Returns titles, URLs, and snippets for matching results."
    )

    BRAVE_API_ENDPOINT: ClassVar[str] = "https://api.search.brave.com/res/v1/web/search"

    @final
    async def run(self, args: WebSearchArgs) -> WebSearchResult:
        """Execute a web search and return results.

        Args:
            args: Search arguments including query and optional count/freshness.

        Returns:
            WebSearchResult with list of result items and metadata.

        Raises:
            ToolError: If API key is missing, invalid, or API request fails.
        """
        self._validate_args(args)
        api_key = self._get_api_key()
        result = await self._execute_search(args, api_key)
        self._update_state(args.query)
        return result

    def _validate_args(self, args: WebSearchArgs) -> None:
        """Validate search arguments."""
        if not args.query.strip():
            raise ToolError("Search query cannot be empty")

        if args.freshness and args.freshness not in {"pd", "pw", "pm", "py"}:
            raise ToolError(
                f"Invalid freshness value: {args.freshness}. "
                "Must be one of: 'pd' (past day), 'pw' (past week), "
                "'pm' (past month), 'py' (past year)"
            )

    def _get_api_key(self) -> str:
        """Get the Brave Search API key from environment.

        Returns:
            The API key string.

        Raises:
            ToolError: If the API key is not set.
        """
        api_key = os.environ.get(self.config.api_key_env_var, "").strip()
        if not api_key:
            raise ToolError(
                f"Brave Search API key not found. "
                f"Set the {self.config.api_key_env_var} environment variable. "
                f"Get a free API key at https://brave.com/search/api/"
            )
        return api_key

    @async_retry(
        tries=3, delay_seconds=1.0, backoff_factor=2.0, is_retryable=_is_retryable_search_error
    )
    async def _execute_search(
        self, args: WebSearchArgs, api_key: str
    ) -> WebSearchResult:
        """Execute the search request to Brave API.

        Args:
            args: Search arguments.
            api_key: The Brave Search API key.

        Returns:
            WebSearchResult with parsed results.

        Raises:
            ToolError: If the API request fails.
        """
        params: dict[str, Any] = {
            "q": args.query,
            "count": args.count,
            "safesearch": self.config.safesearch,
        }

        if args.freshness:
            params["freshness"] = args.freshness

        try:
            async with httpx.AsyncClient(timeout=self.config.timeout) as client:
                response = await client.get(
                    self.BRAVE_API_ENDPOINT,
                    headers={
                        "X-Subscription-Token": api_key,
                        "Accept": "application/json",
                    },
                    params=params,
                )
                response.raise_for_status()
                return self._parse_response(response.json(), args.query)

        except httpx.HTTPStatusError as e:
            match e.response.status_code:
                case 401:
                    raise ToolError(
                        "Invalid Brave Search API key. "
                        "Please check your BRAVE_SEARCH_API_KEY."
                    ) from e
                case 429:
                    raise ToolError(
                        "Brave Search API rate limit exceeded. "
                        "Please wait before making more requests."
                    ) from e
                case _:
                    raise ToolError(
                        f"Brave Search API error: HTTP {e.response.status_code}"
                    ) from e
        except httpx.TimeoutException as e:
            raise ToolError(
                f"Search request timed out after {self.config.timeout}s"
            ) from e
        except httpx.RequestError as e:
            raise ToolError(f"Network error during search: {e}") from e

    def _parse_response(self, data: dict[str, Any], query: str) -> WebSearchResult:
        """Parse the Brave Search API response.

        Args:
            data: Raw JSON response from the API.
            query: The original search query.

        Returns:
            Parsed WebSearchResult.
        """
        results: list[WebSearchResultItem] = []
        web_results = data.get("web", {}).get("results", [])

        for item in web_results:
            title = item.get("title", "")
            url = item.get("url", "")
            description = item.get("description", "")

            if description and len(description) > self.config.max_snippet_length:
                description = description[: self.config.max_snippet_length] + "..."

            if title and url:
                results.append(
                    WebSearchResultItem(title=title, url=url, description=description)
                )

        return WebSearchResult(
            results=results,
            query=query,
            total_count=len(results),
        )

    def _update_state(self, query: str) -> None:
        """Update state with the recent query."""
        self.state.recent_queries.append(query)
        if len(self.state.recent_queries) > 10:
            self.state.recent_queries.pop(0)

    @classmethod
    def get_call_display(cls, event: ToolCallEvent) -> ToolCallDisplay:
        """Generate display info for a web search call."""
        if not isinstance(event.args, WebSearchArgs):
            return ToolCallDisplay(summary="web_search")

        summary = f"web_search: '{event.args.query}'"
        if event.args.count != 10:
            summary += f" (count={event.args.count})"
        if event.args.freshness:
            freshness_labels = {
                "pd": "past day",
                "pw": "past week",
                "pm": "past month",
                "py": "past year",
            }
            label = freshness_labels.get(event.args.freshness, event.args.freshness)
            summary += f" [{label}]"

        return ToolCallDisplay(summary=summary)

    @classmethod
    def get_result_display(cls, event: ToolResultEvent) -> ToolResultDisplay:
        """Generate display info for a web search result."""
        if not isinstance(event.result, WebSearchResult):
            return ToolResultDisplay(
                success=False, message=event.error or event.skip_reason or "No result"
            )

        message = f"Found {event.result.total_count} results for '{event.result.query}'"

        return ToolResultDisplay(success=True, message=message)

    @classmethod
    def get_status_text(cls) -> str:
        """Get status text for UI display."""
        return "Searching the web"
