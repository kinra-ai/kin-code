"""Web fetch tool for retrieving full page content from URLs.

This tool fetches and extracts text content from web pages. It's designed
to be used after web_search to retrieve full content from promising results.
Uses Python's built-in html.parser for content extraction (no extra dependencies).

Example:
    result = await web_fetch.run(WebFetchArgs(url="https://example.com/article"))
    print(result.content)
"""

from __future__ import annotations

from html.parser import HTMLParser
from typing import TYPE_CHECKING, ClassVar, final

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


class WebFetchArgs(BaseModel):
    """Arguments for the web fetch tool."""

    url: str = Field(description="URL to fetch content from")
    max_length: int | None = Field(
        default=None, description="Maximum content length to return (characters)"
    )


class WebFetchResult(BaseModel):
    """Result of a web fetch operation."""

    url: str
    title: str | None
    content: str
    was_truncated: bool


class WebFetchToolConfig(BaseToolConfig):
    """Configuration for the web fetch tool."""

    permission: ToolPermission = ToolPermission.ASK
    timeout: float = Field(default=30.0)
    max_content_bytes: int = Field(default=100_000)
    max_content_chars: int = Field(default=50_000)
    user_agent: str = Field(default="Kin-Code/1.0 (Web Fetch Tool)")
    follow_redirects: bool = Field(default=True)
    max_redirects: int = Field(default=5)


class WebFetchState(BaseToolState):
    """State for the web fetch tool."""

    recent_urls: list[str] = Field(default_factory=list)


class _HTMLTextExtractor(HTMLParser):
    """Extract text content from HTML, skipping script and style tags."""

    SKIP_TAGS: ClassVar[frozenset[str]] = frozenset({
        "script",
        "style",
        "noscript",
        "head",
        "meta",
        "link",
    })

    def __init__(self) -> None:
        super().__init__()
        self.text_chunks: list[str] = []
        self.title: str | None = None
        self._skip_depth = 0
        self._in_title = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        del attrs  # Not used but required by HTMLParser interface
        if tag == "title":
            self._in_title = True
        elif tag in self.SKIP_TAGS:
            self._skip_depth += 1
        elif tag in {"p", "div", "br", "li", "h1", "h2", "h3", "h4", "h5", "h6", "tr"}:
            self.text_chunks.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self._in_title = False
        elif tag in self.SKIP_TAGS:
            self._skip_depth = max(0, self._skip_depth - 1)
        elif tag in {"p", "div", "li", "h1", "h2", "h3", "h4", "h5", "h6"}:
            self.text_chunks.append("\n")

    def handle_data(self, data: str) -> None:
        if self._in_title and not self.title:
            self.title = data.strip()

        if self._skip_depth > 0:
            return

        text = data.strip()
        if text:
            self.text_chunks.append(text + " ")

    def get_text(self) -> str:
        """Get the extracted text, cleaned up."""
        raw_text = "".join(self.text_chunks)
        lines = raw_text.splitlines()
        cleaned_lines = [" ".join(line.split()) for line in lines]
        non_empty_lines = [line for line in cleaned_lines if line]
        return "\n".join(non_empty_lines)


def _is_retryable_fetch_error(e: Exception) -> bool:
    """Check if an exception is retryable for web fetch."""
    if isinstance(e, httpx.HTTPStatusError):
        return e.response.status_code in {408, 429, 500, 502, 503, 504}
    if isinstance(e, httpx.TimeoutException | httpx.ConnectError):
        return True
    return False


class WebFetch(
    BaseTool[WebFetchArgs, WebFetchResult, WebFetchToolConfig, WebFetchState],
    ToolUIData[WebFetchArgs, WebFetchResult],
):
    """Fetch and extract text content from a web page.

    Best used after web_search to retrieve full content from specific URLs.
    Returns plain text, not raw HTML. Large pages are truncated.
    """

    description: ClassVar[str] = (
        "Fetch and extract text content from a web page URL. "
        "Returns plain text content with HTML stripped."
    )

    @final
    async def run(self, args: WebFetchArgs) -> WebFetchResult:
        """Fetch a web page and extract its text content.

        Args:
            args: Fetch arguments including URL and optional max_length.

        Returns:
            WebFetchResult with extracted content and metadata.

        Raises:
            ToolError: If URL is invalid or fetch fails.
        """
        self._validate_args(args)
        result = await self._fetch_and_extract(args)
        self._update_state(args.url)
        return result

    def _validate_args(self, args: WebFetchArgs) -> None:
        """Validate fetch arguments."""
        if not args.url.strip():
            raise ToolError("URL cannot be empty")

        url = args.url.strip()
        if not url.startswith(("http://", "https://")):
            raise ToolError(
                f"Invalid URL: {url}. URL must start with http:// or https://"
            )

        if args.max_length is not None and args.max_length <= 0:
            raise ToolError("max_length must be a positive number")

    @async_retry(
        tries=3,
        delay_seconds=1.0,
        backoff_factor=2.0,
        is_retryable=_is_retryable_fetch_error,
    )
    async def _fetch_and_extract(self, args: WebFetchArgs) -> WebFetchResult:
        """Fetch URL and extract text content.

        Args:
            args: Fetch arguments.

        Returns:
            WebFetchResult with extracted content.

        Raises:
            ToolError: If fetch fails.
        """
        try:
            async with httpx.AsyncClient(
                timeout=self.config.timeout,
                follow_redirects=self.config.follow_redirects,
                max_redirects=self.config.max_redirects,
            ) as client:
                response = await client.get(
                    args.url,
                    headers={
                        "User-Agent": self.config.user_agent,
                        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                    },
                )
                response.raise_for_status()

                content_type = response.headers.get("content-type", "")
                if (
                    "text/html" not in content_type
                    and "application/xhtml" not in content_type
                ):
                    return self._handle_non_html(args.url, response)

                html_bytes = response.content[: self.config.max_content_bytes]
                html_text = html_bytes.decode("utf-8", errors="ignore")

                return self._extract_content(args, html_text)

        except httpx.HTTPStatusError as e:
            match e.response.status_code:
                case 404:
                    raise ToolError(f"Page not found: {args.url}") from e
                case 403:
                    raise ToolError(f"Access forbidden: {args.url}") from e
                case 401:
                    raise ToolError(f"Authentication required: {args.url}") from e
                case _:
                    raise ToolError(
                        f"HTTP error {e.response.status_code} fetching {args.url}"
                    ) from e
        except httpx.TimeoutException as e:
            raise ToolError(
                f"Request timed out after {self.config.timeout}s: {args.url}"
            ) from e
        except httpx.TooManyRedirects as e:
            raise ToolError(
                f"Too many redirects (>{self.config.max_redirects}): {args.url}"
            ) from e
        except httpx.RequestError as e:
            raise ToolError(f"Network error fetching {args.url}: {e}") from e

    def _handle_non_html(self, url: str, response: httpx.Response) -> WebFetchResult:
        """Handle non-HTML content types."""
        content_type = response.headers.get("content-type", "unknown")

        if "text/plain" in content_type:
            content = response.text[: self.config.max_content_chars]
            was_truncated = len(response.text) > self.config.max_content_chars
            return WebFetchResult(
                url=url, title=None, content=content, was_truncated=was_truncated
            )

        return WebFetchResult(
            url=url,
            title=None,
            content=f"[Non-HTML content: {content_type}]",
            was_truncated=False,
        )

    def _extract_content(self, args: WebFetchArgs, html: str) -> WebFetchResult:
        """Extract text content from HTML."""
        extractor = _HTMLTextExtractor()
        try:
            extractor.feed(html)
        except Exception:
            pass

        content = extractor.get_text()
        title = extractor.title

        max_chars = args.max_length or self.config.max_content_chars
        was_truncated = len(content) > max_chars
        if was_truncated:
            content = content[:max_chars] + "\n\n[Content truncated...]"

        return WebFetchResult(
            url=args.url, title=title, content=content, was_truncated=was_truncated
        )

    def _update_state(self, url: str) -> None:
        """Update state with the fetched URL."""
        self.state.recent_urls.append(url)
        if len(self.state.recent_urls) > 10:
            self.state.recent_urls.pop(0)

    @classmethod
    def get_call_display(cls, event: ToolCallEvent) -> ToolCallDisplay:
        """Generate display info for a web fetch call."""
        if not isinstance(event.args, WebFetchArgs):
            return ToolCallDisplay(summary="web_fetch")

        url = event.args.url
        if len(url) > 60:
            url = url[:57] + "..."

        summary = f"web_fetch: {url}"
        if event.args.max_length:
            summary += f" (max {event.args.max_length} chars)"

        return ToolCallDisplay(summary=summary)

    @classmethod
    def get_result_display(cls, event: ToolResultEvent) -> ToolResultDisplay:
        """Generate display info for a web fetch result."""
        if not isinstance(event.result, WebFetchResult):
            return ToolResultDisplay(
                success=False, message=event.error or event.skip_reason or "No result"
            )

        title_str = f" - {event.result.title}" if event.result.title else ""
        message = f"Fetched content from {event.result.url}{title_str}"

        warnings = []
        if event.result.was_truncated:
            warnings.append("Content was truncated due to length limit")

        return ToolResultDisplay(success=True, message=message, warnings=warnings)

    @classmethod
    def get_status_text(cls) -> str:
        """Get status text for UI display."""
        return "Fetching web page"
