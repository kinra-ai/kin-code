from __future__ import annotations

import httpx
import pytest
import respx

from kin_code.core.tools.base import ToolError
from kin_code.core.tools.builtins.web_fetch import (
    WebFetch,
    WebFetchArgs,
    WebFetchResult,
    WebFetchState,
    WebFetchToolConfig,
    _HTMLTextExtractor,
)


@pytest.fixture
def web_fetch():
    config = WebFetchToolConfig()
    return WebFetch(config=config, state=WebFetchState())


class TestHTMLTextExtractor:
    def test_extracts_plain_text(self):
        extractor = _HTMLTextExtractor()
        extractor.feed("<html><body><p>Hello World</p></body></html>")

        text = extractor.get_text()

        assert "Hello World" in text

    def test_extracts_title(self):
        extractor = _HTMLTextExtractor()
        extractor.feed("<html><head><title>Page Title</title></head><body>Content</body></html>")

        assert extractor.title == "Page Title"

    def test_skips_script_tags(self):
        extractor = _HTMLTextExtractor()
        extractor.feed("<html><body><script>alert('xss')</script><p>Safe</p></body></html>")

        text = extractor.get_text()

        assert "alert" not in text
        assert "Safe" in text

    def test_skips_style_tags(self):
        extractor = _HTMLTextExtractor()
        extractor.feed("<html><body><style>.foo { color: red; }</style><p>Visible</p></body></html>")

        text = extractor.get_text()

        assert "color" not in text
        assert "Visible" in text

    def test_adds_newlines_for_block_elements(self):
        extractor = _HTMLTextExtractor()
        extractor.feed("<html><body><p>First</p><p>Second</p></body></html>")

        text = extractor.get_text()

        assert "First" in text
        assert "Second" in text
        lines = text.strip().split("\n")
        assert len(lines) >= 2

    def test_handles_nested_skip_tags(self):
        extractor = _HTMLTextExtractor()
        extractor.feed("<html><body><script><script>nested</script></script><p>Safe</p></body></html>")

        text = extractor.get_text()

        assert "nested" not in text
        assert "Safe" in text

    def test_cleans_whitespace(self):
        extractor = _HTMLTextExtractor()
        extractor.feed("<html><body><p>  Multiple   spaces   here  </p></body></html>")

        text = extractor.get_text()

        assert "Multiple spaces here" in text


def test_get_name():
    assert WebFetch.get_name() == "web_fetch"


@pytest.mark.asyncio
async def test_validates_empty_url(web_fetch):
    with pytest.raises(ToolError) as err:
        await web_fetch.run(WebFetchArgs(url=""))

    assert "empty" in str(err.value).lower()


@pytest.mark.asyncio
async def test_validates_whitespace_url(web_fetch):
    with pytest.raises(ToolError) as err:
        await web_fetch.run(WebFetchArgs(url="   "))

    assert "empty" in str(err.value).lower()


@pytest.mark.asyncio
async def test_validates_url_scheme(web_fetch):
    with pytest.raises(ToolError) as err:
        await web_fetch.run(WebFetchArgs(url="ftp://example.com"))

    assert "http" in str(err.value).lower()


@pytest.mark.asyncio
async def test_validates_negative_max_length(web_fetch):
    with pytest.raises(ToolError) as err:
        await web_fetch.run(WebFetchArgs(url="https://example.com", max_length=-1))

    assert "positive" in str(err.value).lower()


@pytest.mark.asyncio
async def test_validates_zero_max_length(web_fetch):
    with pytest.raises(ToolError) as err:
        await web_fetch.run(WebFetchArgs(url="https://example.com", max_length=0))

    assert "positive" in str(err.value).lower()


@pytest.mark.asyncio
@respx.mock
async def test_successful_fetch(web_fetch):
    html = "<html><head><title>Test Page</title></head><body><p>Hello World</p></body></html>"
    respx.get("https://example.com/page").mock(
        return_value=httpx.Response(200, content=html.encode(), headers={"content-type": "text/html"})
    )

    result = await web_fetch.run(WebFetchArgs(url="https://example.com/page"))

    assert isinstance(result, WebFetchResult)
    assert result.url == "https://example.com/page"
    assert result.title == "Test Page"
    assert "Hello World" in result.content
    assert not result.was_truncated


@pytest.mark.asyncio
@respx.mock
async def test_handles_plain_text(web_fetch):
    respx.get("https://example.com/text.txt").mock(
        return_value=httpx.Response(200, text="Plain text content", headers={"content-type": "text/plain"})
    )

    result = await web_fetch.run(WebFetchArgs(url="https://example.com/text.txt"))

    assert "Plain text content" in result.content


@pytest.mark.asyncio
@respx.mock
async def test_handles_non_html_content(web_fetch):
    respx.get("https://example.com/file.pdf").mock(
        return_value=httpx.Response(200, content=b"PDF content", headers={"content-type": "application/pdf"})
    )

    result = await web_fetch.run(WebFetchArgs(url="https://example.com/file.pdf"))

    assert "Non-HTML content" in result.content
    assert "application/pdf" in result.content


@pytest.mark.asyncio
@respx.mock
async def test_handles_404_not_found(web_fetch):
    respx.get("https://example.com/missing").mock(
        return_value=httpx.Response(404)
    )

    with pytest.raises(ToolError) as err:
        await web_fetch.run(WebFetchArgs(url="https://example.com/missing"))

    assert "not found" in str(err.value).lower()


@pytest.mark.asyncio
@respx.mock
async def test_handles_403_forbidden(web_fetch):
    respx.get("https://example.com/forbidden").mock(
        return_value=httpx.Response(403)
    )

    with pytest.raises(ToolError) as err:
        await web_fetch.run(WebFetchArgs(url="https://example.com/forbidden"))

    assert "forbidden" in str(err.value).lower()


@pytest.mark.asyncio
@respx.mock
async def test_handles_401_unauthorized(web_fetch):
    respx.get("https://example.com/protected").mock(
        return_value=httpx.Response(401)
    )

    with pytest.raises(ToolError) as err:
        await web_fetch.run(WebFetchArgs(url="https://example.com/protected"))

    assert "authentication" in str(err.value).lower()


@pytest.mark.asyncio
@respx.mock
async def test_truncates_long_content(web_fetch):
    config = WebFetchToolConfig(max_content_chars=100)
    tool = WebFetch(config=config, state=WebFetchState())

    long_content = "<html><body>" + "x" * 200 + "</body></html>"
    respx.get("https://example.com/long").mock(
        return_value=httpx.Response(200, content=long_content.encode(), headers={"content-type": "text/html"})
    )

    result = await tool.run(WebFetchArgs(url="https://example.com/long"))

    assert result.was_truncated
    assert "[Content truncated...]" in result.content


@pytest.mark.asyncio
@respx.mock
async def test_respects_max_length_parameter(web_fetch):
    long_content = "<html><body>" + "x" * 500 + "</body></html>"
    respx.get("https://example.com/long").mock(
        return_value=httpx.Response(200, content=long_content.encode(), headers={"content-type": "text/html"})
    )

    result = await web_fetch.run(WebFetchArgs(url="https://example.com/long", max_length=50))

    assert result.was_truncated
    assert len(result.content) <= 100  # 50 + "[Content truncated...]"


@pytest.mark.asyncio
@respx.mock
async def test_tracks_recent_urls(web_fetch):
    html = "<html><body>Content</body></html>"
    respx.get(url__regex=r"https://example\.com/page\d").mock(
        return_value=httpx.Response(200, content=html.encode(), headers={"content-type": "text/html"})
    )

    await web_fetch.run(WebFetchArgs(url="https://example.com/page1"))
    await web_fetch.run(WebFetchArgs(url="https://example.com/page2"))
    await web_fetch.run(WebFetchArgs(url="https://example.com/page3"))

    assert web_fetch.state.recent_urls == [
        "https://example.com/page1",
        "https://example.com/page2",
        "https://example.com/page3",
    ]


@pytest.mark.asyncio
@respx.mock
async def test_limits_recent_urls_history(web_fetch):
    html = "<html><body>Content</body></html>"
    respx.get(url__regex=r"https://example\.com/page\d+").mock(
        return_value=httpx.Response(200, content=html.encode(), headers={"content-type": "text/html"})
    )

    for i in range(15):
        await web_fetch.run(WebFetchArgs(url=f"https://example.com/page{i}"))

    assert len(web_fetch.state.recent_urls) == 10
    assert web_fetch.state.recent_urls[0] == "https://example.com/page5"
    assert web_fetch.state.recent_urls[-1] == "https://example.com/page14"


@pytest.mark.asyncio
@respx.mock
async def test_sends_correct_headers(web_fetch):
    route = respx.get("https://example.com/page").mock(
        return_value=httpx.Response(200, content=b"<html></html>", headers={"content-type": "text/html"})
    )

    await web_fetch.run(WebFetchArgs(url="https://example.com/page"))

    request = route.calls[0].request
    assert "Kin-Code" in request.headers.get("User-Agent", "")


def test_get_call_display_basic():
    from kin_code.core.types import ToolCallEvent

    args = WebFetchArgs(url="https://example.com/page")
    event = ToolCallEvent(
        tool_name="web_fetch",
        tool_call_id="123",
        args=args,
        tool_class=WebFetch,
    )

    display = WebFetch.get_call_display(event)

    assert "example.com" in display.summary


def test_get_call_display_long_url():
    from kin_code.core.types import ToolCallEvent

    long_url = "https://example.com/" + "x" * 100
    args = WebFetchArgs(url=long_url)
    event = ToolCallEvent(
        tool_name="web_fetch",
        tool_call_id="123",
        args=args,
        tool_class=WebFetch,
    )

    display = WebFetch.get_call_display(event)

    assert len(display.summary) < 100
    assert "..." in display.summary


def test_get_result_display():
    from kin_code.core.types import ToolResultEvent

    result = WebFetchResult(
        url="https://example.com/page",
        title="Example Page",
        content="Some content",
        was_truncated=False,
    )
    event = ToolResultEvent(
        tool_name="web_fetch",
        tool_call_id="123",
        result=result,
        error=None,
        skipped=False,
        skip_reason=None,
        tool_class=WebFetch,
    )

    display = WebFetch.get_result_display(event)

    assert display.success
    assert "Example Page" in display.message


def test_get_result_display_truncated():
    from kin_code.core.types import ToolResultEvent

    result = WebFetchResult(
        url="https://example.com/page",
        title=None,
        content="Truncated content",
        was_truncated=True,
    )
    event = ToolResultEvent(
        tool_name="web_fetch",
        tool_call_id="123",
        result=result,
        error=None,
        skipped=False,
        skip_reason=None,
        tool_class=WebFetch,
    )

    display = WebFetch.get_result_display(event)

    assert display.success
    assert len(display.warnings) == 1
    assert "truncated" in display.warnings[0].lower()


def test_get_status_text():
    assert WebFetch.get_status_text() == "Fetching web page"
