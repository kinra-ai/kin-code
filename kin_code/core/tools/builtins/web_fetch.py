"""Web fetch tool for retrieving and processing web page content."""

from __future__ import annotations

from collections.abc import AsyncGenerator
from html.parser import HTMLParser
import json
import re
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


class _HTMLTextExtractor(HTMLParser):
    """Extract text content from HTML, stripping scripts, styles, and tags."""

    def __init__(self) -> None:
        super().__init__()
        self._text_parts: list[str] = []
        self._skip_depth = 0
        self._skip_tags = {"script", "style", "noscript", "svg", "path"}

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() in self._skip_tags:
            self._skip_depth += 1

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() in self._skip_tags and self._skip_depth > 0:
            self._skip_depth -= 1

    def handle_data(self, data: str) -> None:
        if self._skip_depth == 0:
            text = data.strip()
            if text:
                self._text_parts.append(text)

    def get_text(self) -> str:
        return " ".join(self._text_parts)


def _extract_text_from_html(html: str) -> str:
    """Extract readable text from HTML content."""
    parser = _HTMLTextExtractor()
    try:
        parser.feed(html)
        text = parser.get_text()
    except Exception:
        # Fallback: strip all tags with regex
        text = re.sub(r"<[^>]+>", " ", html)
        text = re.sub(r"\s+", " ", text).strip()

    return text


class WebFetchConfig(BaseToolConfig):
    """Configuration for the web fetch tool."""

    permission: ToolPermission = ToolPermission.ALWAYS
    max_bytes: int = Field(
        default=100_000, description="Maximum content bytes to retrieve"
    )
    timeout: int = Field(default=30, description="Request timeout in seconds")


class WebFetchArgs(BaseModel):
    """Arguments for web fetch."""

    url: str = Field(description="URL to fetch content from")
    max_bytes: int | None = Field(
        default=None, description="Maximum content bytes (default: 100KB)"
    )


class WebFetchResult(BaseModel):
    """Result from web fetch."""

    url: str
    final_url: str
    content: str
    content_type: str
    was_truncated: bool


class WebFetch(
    BaseTool[WebFetchArgs, WebFetchResult, WebFetchConfig, BaseToolState],
    ToolUIData[WebFetchArgs, WebFetchResult],
):
    """Fetch and extract text content from a URL."""

    description: ClassVar[str] = """Fetch content from a URL and extract readable text.

USE WHEN:
- Reading documentation from a specific URL
- Fetching API responses or data from known endpoints
- Following up on URLs from web search results
- Retrieving content from a page the user referenced

DO NOT USE WHEN:
- You need to find information (use web_search first)
- Reading local files (use read_file)
- The URL is unknown or needs to be discovered

EXAMPLES:
- Fetch Python docs: url="https://docs.python.org/3/library/asyncio.html"
- Read a GitHub README: url="https://github.com/user/repo/blob/main/README.md"
- Get JSON from an API: url="https://api.example.com/data.json"

NOTES:
- HTML pages have tags stripped, returning readable text
- JSON responses are pretty-printed for readability
- Content is truncated if it exceeds max_bytes"""

    @classmethod
    def get_call_display(cls, event: ToolCallEvent) -> ToolCallDisplay:
        if not isinstance(event.args, WebFetchArgs):
            return ToolCallDisplay(summary="web_fetch")
        # Show just the domain for cleaner display
        url = event.args.url
        try:
            from urllib.parse import urlparse

            domain = urlparse(url).netloc
            return ToolCallDisplay(summary=f"Fetching: {domain}")
        except Exception:
            return ToolCallDisplay(summary=f"Fetching: {url[:50]}")

    @classmethod
    def get_result_display(cls, event: ToolResultEvent) -> ToolResultDisplay:
        if not isinstance(event.result, WebFetchResult):
            return ToolResultDisplay(
                success=False, message=event.error or event.skip_reason or "No result"
            )

        result = event.result
        message = f"Fetched {len(result.content)} chars"
        if result.was_truncated:
            message += " (truncated)"

        return ToolResultDisplay(success=True, message=message)

    @classmethod
    def get_status_text(cls) -> str:
        return "Fetching URL"

    async def run(
        self, args: WebFetchArgs, ctx: InvokeContext | None = None
    ) -> AsyncGenerator[ToolStreamEvent | WebFetchResult, None]:
        url = args.url.strip()
        if not url:
            raise ToolError("URL cannot be empty")

        # Basic URL validation
        if not url.startswith(("http://", "https://")):
            raise ToolError(
                f"Invalid URL: {url}. URL must start with http:// or https://"
            )

        max_bytes = args.max_bytes or self.config.max_bytes

        async with httpx.AsyncClient(
            timeout=self.config.timeout, follow_redirects=True
        ) as client:
            try:
                response = await client.get(url)
                response.raise_for_status()
            except httpx.TimeoutException:
                raise ToolError(f"Request timed out after {self.config.timeout}s")
            except httpx.HTTPStatusError as e:
                raise ToolError(f"HTTP error {e.response.status_code}: {url}")
            except httpx.RequestError as e:
                raise ToolError(f"Request failed: {e}") from e

        content_type = response.headers.get("content-type", "").lower()
        final_url = str(response.url)
        raw_content = response.text

        # Process content based on type
        if "application/json" in content_type:
            try:
                parsed = json.loads(raw_content)
                content = json.dumps(parsed, indent=2)
            except json.JSONDecodeError:
                content = raw_content
        elif "text/html" in content_type:
            content = _extract_text_from_html(raw_content)
        else:
            # Plain text or other - return as-is
            content = raw_content

        # Truncate if needed
        was_truncated = len(content) > max_bytes
        if was_truncated:
            content = content[:max_bytes]

        yield WebFetchResult(
            url=url,
            final_url=final_url,
            content=content,
            content_type=content_type,
            was_truncated=was_truncated,
        )
