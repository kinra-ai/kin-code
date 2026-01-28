"""Tests for the web_search tool."""

from __future__ import annotations

import httpx
import pytest
import respx

from kin_code.core.tools.base import BaseToolState, ToolError
from kin_code.core.tools.builtins.web_search import (
    BRAVE_API_KEY_ENV,
    BRAVE_SEARCH_URL,
    WebSearch,
    WebSearchArgs,
    WebSearchConfig,
    WebSearchResult,
)
from tests.mock.utils import collect_result


@pytest.fixture
def web_search(monkeypatch):
    """Create a WebSearch tool instance with mocked API key."""
    monkeypatch.setenv(BRAVE_API_KEY_ENV, "test-api-key")
    return WebSearch(config=WebSearchConfig(), state=BaseToolState())


@pytest.fixture
def mock_brave_response():
    """Sample Brave Search API response."""
    return {
        "web": {
            "results": [
                {
                    "title": "Python Documentation",
                    "url": "https://docs.python.org/",
                    "description": "Official Python documentation",
                },
                {
                    "title": "Python Tutorial",
                    "url": "https://python.org/tutorial/",
                    "description": "Learn Python basics",
                },
            ]
        }
    }


@pytest.mark.asyncio
async def test_raises_error_without_api_key(monkeypatch):
    """Should raise ToolError when BRAVE_API_KEY is not set."""
    monkeypatch.delenv(BRAVE_API_KEY_ENV, raising=False)
    tool = WebSearch(config=WebSearchConfig(), state=BaseToolState())

    with pytest.raises(ToolError) as err:
        await collect_result(tool.run(WebSearchArgs(query="test")))

    assert BRAVE_API_KEY_ENV in str(err.value)


@pytest.mark.asyncio
async def test_raises_error_with_empty_query(web_search):
    """Should raise ToolError for empty query."""
    with pytest.raises(ToolError) as err:
        await collect_result(web_search.run(WebSearchArgs(query="")))

    assert "cannot be empty" in str(err.value)


@pytest.mark.asyncio
async def test_raises_error_with_whitespace_query(web_search):
    """Should raise ToolError for whitespace-only query."""
    with pytest.raises(ToolError) as err:
        await collect_result(web_search.run(WebSearchArgs(query="   ")))

    assert "cannot be empty" in str(err.value)


@pytest.mark.asyncio
async def test_returns_search_results(web_search, mock_brave_response):
    """Should return parsed search results."""
    with respx.mock:
        respx.get(BRAVE_SEARCH_URL).mock(
            return_value=httpx.Response(200, json=mock_brave_response)
        )

        result = await collect_result(web_search.run(WebSearchArgs(query="python")))

    assert isinstance(result, WebSearchResult)
    assert result.query == "python"
    assert result.total_count == 2
    assert len(result.results) == 2
    assert result.results[0].title == "Python Documentation"
    assert result.results[0].url == "https://docs.python.org/"


@pytest.mark.asyncio
async def test_handles_empty_results(web_search):
    """Should handle empty search results gracefully."""
    with respx.mock:
        respx.get(BRAVE_SEARCH_URL).mock(
            return_value=httpx.Response(200, json={"web": {"results": []}})
        )

        result = await collect_result(
            web_search.run(WebSearchArgs(query="nonexistent"))
        )

    assert result.total_count == 0
    assert result.results == []


@pytest.mark.asyncio
async def test_handles_missing_web_key(web_search):
    """Should handle response without 'web' key."""
    with respx.mock:
        respx.get(BRAVE_SEARCH_URL).mock(return_value=httpx.Response(200, json={}))

        result = await collect_result(web_search.run(WebSearchArgs(query="test")))

    assert result.total_count == 0
    assert result.results == []


@pytest.mark.asyncio
async def test_respects_count_parameter(web_search, mock_brave_response):
    """Should pass count parameter to API."""
    with respx.mock:
        route = respx.get(BRAVE_SEARCH_URL).mock(
            return_value=httpx.Response(200, json=mock_brave_response)
        )

        await collect_result(web_search.run(WebSearchArgs(query="test", count=5)))

        assert route.called
        request = route.calls[0].request
        assert "count=5" in str(request.url)


@pytest.mark.asyncio
async def test_sends_correct_headers(web_search, mock_brave_response):
    """Should send correct API headers."""
    with respx.mock:
        route = respx.get(BRAVE_SEARCH_URL).mock(
            return_value=httpx.Response(200, json=mock_brave_response)
        )

        await collect_result(web_search.run(WebSearchArgs(query="test")))

        request = route.calls[0].request
        assert request.headers["X-Subscription-Token"] == "test-api-key"
        assert request.headers["Accept"] == "application/json"


@pytest.mark.asyncio
async def test_handles_401_unauthorized(web_search):
    """Should raise ToolError for invalid API key."""
    with respx.mock:
        respx.get(BRAVE_SEARCH_URL).mock(return_value=httpx.Response(401))

        with pytest.raises(ToolError) as err:
            await collect_result(web_search.run(WebSearchArgs(query="test")))

    assert "Invalid" in str(err.value)


@pytest.mark.asyncio
async def test_handles_429_rate_limit(web_search):
    """Should raise ToolError for rate limiting."""
    with respx.mock:
        respx.get(BRAVE_SEARCH_URL).mock(return_value=httpx.Response(429))

        with pytest.raises(ToolError) as err:
            await collect_result(web_search.run(WebSearchArgs(query="test")))

    assert "rate limit" in str(err.value)


@pytest.mark.asyncio
async def test_handles_timeout(web_search):
    """Should raise ToolError on timeout."""
    with respx.mock:
        respx.get(BRAVE_SEARCH_URL).mock(side_effect=httpx.TimeoutException("Timeout"))

        with pytest.raises(ToolError) as err:
            await collect_result(web_search.run(WebSearchArgs(query="test")))

    assert "timed out" in str(err.value)


@pytest.mark.asyncio
async def test_handles_request_error(web_search):
    """Should raise ToolError on request failure."""
    with respx.mock:
        respx.get(BRAVE_SEARCH_URL).mock(
            side_effect=httpx.RequestError("Connection failed")
        )

        with pytest.raises(ToolError) as err:
            await collect_result(web_search.run(WebSearchArgs(query="test")))

    assert "failed" in str(err.value)


@pytest.mark.asyncio
async def test_skips_results_without_title(web_search):
    """Should skip results that lack a title."""
    with respx.mock:
        respx.get(BRAVE_SEARCH_URL).mock(
            return_value=httpx.Response(
                200,
                json={
                    "web": {
                        "results": [
                            {"url": "https://no-title.com/", "description": "No title"},
                            {
                                "title": "Has Title",
                                "url": "https://has-title.com/",
                                "description": "Has title",
                            },
                        ]
                    }
                },
            )
        )

        result = await collect_result(web_search.run(WebSearchArgs(query="test")))

    assert result.total_count == 1
    assert result.results[0].title == "Has Title"


@pytest.mark.asyncio
async def test_skips_results_without_url(web_search):
    """Should skip results that lack a URL."""
    with respx.mock:
        respx.get(BRAVE_SEARCH_URL).mock(
            return_value=httpx.Response(
                200,
                json={
                    "web": {
                        "results": [
                            {"title": "No URL", "description": "Missing URL"},
                            {
                                "title": "Has URL",
                                "url": "https://has-url.com/",
                                "description": "Has URL",
                            },
                        ]
                    }
                },
            )
        )

        result = await collect_result(web_search.run(WebSearchArgs(query="test")))

    assert result.total_count == 1
    assert result.results[0].url == "https://has-url.com/"


class TestToolUIData:
    """Test UI display methods."""

    def test_get_call_display(self):
        from kin_code.core.types import ToolCallEvent

        event = ToolCallEvent(
            tool_name="web_search",
            tool_class=WebSearch,
            tool_call_id="test-id",
            args=WebSearchArgs(query="python docs"),
        )
        display = WebSearch.get_call_display(event)

        assert "python docs" in display.summary

    def test_get_result_display(self):
        from kin_code.core.types import ToolResultEvent

        result = WebSearchResult(query="python", results=[], total_count=5)
        event = ToolResultEvent(
            tool_name="web_search",
            tool_class=WebSearch,
            tool_call_id="test-id",
            result=result,
        )
        display = WebSearch.get_result_display(event)

        assert display.success
        assert "5" in display.message

    def test_get_status_text(self):
        assert "web" in WebSearch.get_status_text().lower()
