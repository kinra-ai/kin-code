"""Tests for the web_fetch tool."""

from __future__ import annotations

import httpx
import pytest
import respx

from kin_code.core.tools.base import BaseToolState, ToolError
from kin_code.core.tools.builtins.web_fetch import (
    WebFetch,
    WebFetchArgs,
    WebFetchConfig,
    WebFetchResult,
    _extract_text_from_html,
)
from tests.mock.utils import collect_result


@pytest.fixture
def web_fetch():
    """Create a WebFetch tool instance."""
    return WebFetch(config=WebFetchConfig(), state=BaseToolState())


class TestHTMLExtraction:
    """Test the HTML text extraction helper."""

    def test_extracts_text_from_simple_html(self):
        html = "<html><body><p>Hello World</p></body></html>"
        result = _extract_text_from_html(html)
        assert "Hello World" in result

    def test_strips_script_tags(self):
        html = "<html><body><script>alert('bad')</script><p>Content</p></body></html>"
        result = _extract_text_from_html(html)
        assert "Content" in result
        assert "alert" not in result

    def test_strips_style_tags(self):
        html = "<html><body><style>.foo{color:red}</style><p>Content</p></body></html>"
        result = _extract_text_from_html(html)
        assert "Content" in result
        assert "color" not in result

    def test_strips_noscript_tags(self):
        html = "<html><body><noscript>Enable JS</noscript><p>Content</p></body></html>"
        result = _extract_text_from_html(html)
        assert "Content" in result
        assert "Enable JS" not in result

    def test_handles_nested_tags(self):
        html = "<div><span><strong>Bold text</strong></span></div>"
        result = _extract_text_from_html(html)
        assert "Bold text" in result

    def test_handles_empty_html(self):
        result = _extract_text_from_html("")
        assert result == ""

    def test_handles_malformed_html(self):
        html = "<p>Unclosed tag<div>More text"
        result = _extract_text_from_html(html)
        assert "Unclosed tag" in result or "More text" in result


class TestWebFetchValidation:
    """Test input validation."""

    @pytest.mark.asyncio
    async def test_raises_error_for_empty_url(self, web_fetch):
        with pytest.raises(ToolError) as err:
            await collect_result(web_fetch.run(WebFetchArgs(url="")))

        assert "cannot be empty" in str(err.value)

    @pytest.mark.asyncio
    async def test_raises_error_for_whitespace_url(self, web_fetch):
        with pytest.raises(ToolError) as err:
            await collect_result(web_fetch.run(WebFetchArgs(url="   ")))

        assert "cannot be empty" in str(err.value)

    @pytest.mark.asyncio
    async def test_raises_error_for_invalid_url_scheme(self, web_fetch):
        with pytest.raises(ToolError) as err:
            await collect_result(web_fetch.run(WebFetchArgs(url="ftp://example.com")))

        assert "Invalid URL" in str(err.value)

    @pytest.mark.asyncio
    async def test_raises_error_for_no_scheme(self, web_fetch):
        with pytest.raises(ToolError) as err:
            await collect_result(web_fetch.run(WebFetchArgs(url="example.com")))

        assert "Invalid URL" in str(err.value)


class TestWebFetchHTTP:
    """Test HTTP request handling."""

    @pytest.mark.asyncio
    async def test_fetches_html_content(self, web_fetch):
        html = "<html><body><p>Hello World</p></body></html>"
        with respx.mock:
            respx.get("https://example.com/").mock(
                return_value=httpx.Response(
                    200, text=html, headers={"content-type": "text/html"}
                )
            )

            result = await collect_result(
                web_fetch.run(WebFetchArgs(url="https://example.com/"))
            )

        assert isinstance(result, WebFetchResult)
        assert "Hello World" in result.content
        assert "text/html" in result.content_type

    @pytest.mark.asyncio
    async def test_fetches_json_content(self, web_fetch):
        data = {"key": "value", "number": 42}
        with respx.mock:
            respx.get("https://api.example.com/data").mock(
                return_value=httpx.Response(
                    200, json=data, headers={"content-type": "application/json"}
                )
            )

            result = await collect_result(
                web_fetch.run(WebFetchArgs(url="https://api.example.com/data"))
            )

        assert "key" in result.content
        assert "value" in result.content
        assert "application/json" in result.content_type

    @pytest.mark.asyncio
    async def test_pretty_prints_json(self, web_fetch):
        data = {"nested": {"key": "value"}}
        with respx.mock:
            respx.get("https://api.example.com/").mock(
                return_value=httpx.Response(
                    200, json=data, headers={"content-type": "application/json"}
                )
            )

            result = await collect_result(
                web_fetch.run(WebFetchArgs(url="https://api.example.com/"))
            )

        # Pretty-printed JSON has newlines
        assert "\n" in result.content

    @pytest.mark.asyncio
    async def test_fetches_plain_text(self, web_fetch):
        with respx.mock:
            respx.get("https://example.com/file.txt").mock(
                return_value=httpx.Response(
                    200,
                    text="Plain text content",
                    headers={"content-type": "text/plain"},
                )
            )

            result = await collect_result(
                web_fetch.run(WebFetchArgs(url="https://example.com/file.txt"))
            )

        assert result.content == "Plain text content"
        assert "text/plain" in result.content_type

    @pytest.mark.asyncio
    async def test_follows_redirects(self, web_fetch):
        with respx.mock:
            # respx handles follow_redirects by returning the final response
            respx.get("https://example.com/redirect").mock(
                return_value=httpx.Response(
                    200,
                    text="Final content",
                    headers={"content-type": "text/plain"},
                    # Note: respx doesn't simulate redirect chains well,
                    # but we can test that the original URL is preserved
                )
            )

            result = await collect_result(
                web_fetch.run(WebFetchArgs(url="https://example.com/redirect"))
            )

        assert result.url == "https://example.com/redirect"
        assert "Final content" in result.content

    @pytest.mark.asyncio
    async def test_truncates_large_content(self, web_fetch):
        large_content = "x" * 200_000  # 200KB
        with respx.mock:
            respx.get("https://example.com/").mock(
                return_value=httpx.Response(
                    200, text=large_content, headers={"content-type": "text/plain"}
                )
            )

            result = await collect_result(
                web_fetch.run(WebFetchArgs(url="https://example.com/", max_bytes=1000))
            )

        assert len(result.content) == 1000
        assert result.was_truncated

    @pytest.mark.asyncio
    async def test_handles_timeout(self, web_fetch):
        with respx.mock:
            respx.get("https://slow.example.com/").mock(
                side_effect=httpx.TimeoutException("Timeout")
            )

            with pytest.raises(ToolError) as err:
                await collect_result(
                    web_fetch.run(WebFetchArgs(url="https://slow.example.com/"))
                )

        assert "timed out" in str(err.value)

    @pytest.mark.asyncio
    async def test_handles_http_error(self, web_fetch):
        with respx.mock:
            respx.get("https://example.com/missing").mock(
                return_value=httpx.Response(404)
            )

            with pytest.raises(ToolError) as err:
                await collect_result(
                    web_fetch.run(WebFetchArgs(url="https://example.com/missing"))
                )

        assert "404" in str(err.value)

    @pytest.mark.asyncio
    async def test_handles_request_error(self, web_fetch):
        with respx.mock:
            respx.get("https://down.example.com/").mock(
                side_effect=httpx.RequestError("Connection refused")
            )

            with pytest.raises(ToolError) as err:
                await collect_result(
                    web_fetch.run(WebFetchArgs(url="https://down.example.com/"))
                )

        assert "failed" in str(err.value)

    @pytest.mark.asyncio
    async def test_handles_invalid_json(self, web_fetch):
        with respx.mock:
            respx.get("https://api.example.com/").mock(
                return_value=httpx.Response(
                    200,
                    text="not valid json {",
                    headers={"content-type": "application/json"},
                )
            )

            result = await collect_result(
                web_fetch.run(WebFetchArgs(url="https://api.example.com/"))
            )

        # Should return raw content when JSON parsing fails
        assert result.content == "not valid json {"


class TestToolUIData:
    """Test UI display methods."""

    def test_get_call_display_shows_domain(self):
        from kin_code.core.types import ToolCallEvent

        event = ToolCallEvent(
            tool_name="web_fetch",
            tool_class=WebFetch,
            tool_call_id="test-id",
            args=WebFetchArgs(url="https://docs.python.org/3/library/"),
        )
        display = WebFetch.get_call_display(event)

        assert "docs.python.org" in display.summary

    def test_get_result_display_shows_size(self):
        from kin_code.core.types import ToolResultEvent

        result = WebFetchResult(
            url="https://example.com",
            final_url="https://example.com",
            content="x" * 5000,
            content_type="text/html",
            was_truncated=False,
        )
        event = ToolResultEvent(
            tool_name="web_fetch",
            tool_class=WebFetch,
            tool_call_id="test-id",
            result=result,
        )
        display = WebFetch.get_result_display(event)

        assert display.success
        assert "5000" in display.message

    def test_get_result_display_shows_truncated(self):
        from kin_code.core.types import ToolResultEvent

        result = WebFetchResult(
            url="https://example.com",
            final_url="https://example.com",
            content="truncated",
            content_type="text/html",
            was_truncated=True,
        )
        event = ToolResultEvent(
            tool_name="web_fetch",
            tool_class=WebFetch,
            tool_call_id="test-id",
            result=result,
        )
        display = WebFetch.get_result_display(event)

        assert "truncated" in display.message.lower()

    def test_get_status_text(self):
        assert "Fetch" in WebFetch.get_status_text()
