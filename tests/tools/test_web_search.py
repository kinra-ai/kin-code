from __future__ import annotations

import httpx
import pytest
import respx

from kin_code.core.tools.base import ToolError
from kin_code.core.tools.builtins.web_search import (
    WebSearch,
    WebSearchArgs,
    WebSearchResult,
    WebSearchState,
    WebSearchToolConfig,
)


@pytest.fixture
def web_search(monkeypatch):
    monkeypatch.setenv("BRAVE_SEARCH_API_KEY", "test-api-key")
    config = WebSearchToolConfig()
    return WebSearch(config=config, state=WebSearchState())


@pytest.fixture
def mock_brave_api():
    with respx.mock:
        yield respx.route(host="api.search.brave.com")


@pytest.fixture
def sample_api_response():
    return {
        "web": {
            "results": [
                {
                    "title": "Python Tutorial",
                    "url": "https://python.org/tutorial",
                    "description": "Learn Python programming from the official tutorial.",
                },
                {
                    "title": "Python Documentation",
                    "url": "https://docs.python.org",
                    "description": "Official Python documentation and reference.",
                },
            ]
        }
    }


def test_get_name():
    assert WebSearch.get_name() == "web_search"


def test_requires_api_key(monkeypatch):
    monkeypatch.delenv("BRAVE_SEARCH_API_KEY", raising=False)
    config = WebSearchToolConfig()
    tool = WebSearch(config=config, state=WebSearchState())

    with pytest.raises(ToolError) as err:
        tool._get_api_key()

    assert "BRAVE_SEARCH_API_KEY" in str(err.value)
    assert "brave.com/search/api" in str(err.value)


@pytest.mark.asyncio
async def test_validates_empty_query(web_search):
    with pytest.raises(ToolError) as err:
        await web_search.run(WebSearchArgs(query=""))

    assert "empty" in str(err.value).lower()


@pytest.mark.asyncio
async def test_validates_whitespace_query(web_search):
    with pytest.raises(ToolError) as err:
        await web_search.run(WebSearchArgs(query="   "))

    assert "empty" in str(err.value).lower()


@pytest.mark.asyncio
async def test_validates_invalid_freshness(web_search):
    with pytest.raises(ToolError) as err:
        await web_search.run(WebSearchArgs(query="test", freshness="invalid"))

    assert "freshness" in str(err.value).lower()


@pytest.mark.asyncio
@respx.mock
async def test_successful_search(web_search, sample_api_response):
    respx.get("https://api.search.brave.com/res/v1/web/search").mock(
        return_value=httpx.Response(200, json=sample_api_response)
    )

    result = await web_search.run(WebSearchArgs(query="python tutorial"))

    assert isinstance(result, WebSearchResult)
    assert result.query == "python tutorial"
    assert result.total_count == 2
    assert len(result.results) == 2
    assert result.results[0].title == "Python Tutorial"
    assert result.results[0].url == "https://python.org/tutorial"


@pytest.mark.asyncio
@respx.mock
async def test_respects_count_parameter(web_search, sample_api_response):
    route = respx.get("https://api.search.brave.com/res/v1/web/search").mock(
        return_value=httpx.Response(200, json=sample_api_response)
    )

    await web_search.run(WebSearchArgs(query="test", count=5))

    assert route.called
    request = route.calls[0].request
    assert b"count=5" in request.url.query


@pytest.mark.asyncio
@respx.mock
async def test_respects_freshness_parameter(web_search, sample_api_response):
    route = respx.get("https://api.search.brave.com/res/v1/web/search").mock(
        return_value=httpx.Response(200, json=sample_api_response)
    )

    await web_search.run(WebSearchArgs(query="test", freshness="pd"))

    assert route.called
    request = route.calls[0].request
    assert b"freshness=pd" in request.url.query


@pytest.mark.asyncio
@respx.mock
async def test_handles_empty_results(web_search):
    respx.get("https://api.search.brave.com/res/v1/web/search").mock(
        return_value=httpx.Response(200, json={"web": {"results": []}})
    )

    result = await web_search.run(WebSearchArgs(query="nonexistent query"))

    assert result.total_count == 0
    assert len(result.results) == 0


@pytest.mark.asyncio
@respx.mock
async def test_handles_401_unauthorized(web_search):
    respx.get("https://api.search.brave.com/res/v1/web/search").mock(
        return_value=httpx.Response(401)
    )

    with pytest.raises(ToolError) as err:
        await web_search.run(WebSearchArgs(query="test"))

    assert "invalid" in str(err.value).lower() or "api key" in str(err.value).lower()


@pytest.mark.asyncio
@respx.mock
async def test_handles_429_rate_limit(web_search):
    respx.get("https://api.search.brave.com/res/v1/web/search").mock(
        return_value=httpx.Response(429)
    )

    with pytest.raises(ToolError) as err:
        await web_search.run(WebSearchArgs(query="test"))

    assert "rate limit" in str(err.value).lower()


@pytest.mark.asyncio
@respx.mock
async def test_handles_500_server_error(web_search):
    respx.get("https://api.search.brave.com/res/v1/web/search").mock(
        return_value=httpx.Response(500)
    )

    with pytest.raises(ToolError) as err:
        await web_search.run(WebSearchArgs(query="test"))

    assert "500" in str(err.value)


@pytest.mark.asyncio
@respx.mock
async def test_truncates_long_descriptions(monkeypatch):
    monkeypatch.setenv("BRAVE_SEARCH_API_KEY", "test-key")
    config = WebSearchToolConfig(max_snippet_length=50)
    tool = WebSearch(config=config, state=WebSearchState())

    long_description = "x" * 100
    respx.get("https://api.search.brave.com/res/v1/web/search").mock(
        return_value=httpx.Response(
            200,
            json={
                "web": {
                    "results": [
                        {
                            "title": "Test",
                            "url": "https://test.com",
                            "description": long_description,
                        }
                    ]
                }
            },
        )
    )

    result = await tool.run(WebSearchArgs(query="test"))

    assert len(result.results[0].description) <= 53  # 50 + "..."


@pytest.mark.asyncio
@respx.mock
async def test_tracks_recent_queries(web_search, sample_api_response):
    respx.get("https://api.search.brave.com/res/v1/web/search").mock(
        return_value=httpx.Response(200, json=sample_api_response)
    )

    await web_search.run(WebSearchArgs(query="first"))
    await web_search.run(WebSearchArgs(query="second"))
    await web_search.run(WebSearchArgs(query="third"))

    assert web_search.state.recent_queries == ["first", "second", "third"]


@pytest.mark.asyncio
@respx.mock
async def test_limits_recent_queries_history(web_search, sample_api_response):
    respx.get("https://api.search.brave.com/res/v1/web/search").mock(
        return_value=httpx.Response(200, json=sample_api_response)
    )

    for i in range(15):
        await web_search.run(WebSearchArgs(query=f"query{i}"))

    assert len(web_search.state.recent_queries) == 10
    assert web_search.state.recent_queries[0] == "query5"
    assert web_search.state.recent_queries[-1] == "query14"


@pytest.mark.asyncio
@respx.mock
async def test_sends_correct_headers(web_search, sample_api_response):
    route = respx.get("https://api.search.brave.com/res/v1/web/search").mock(
        return_value=httpx.Response(200, json=sample_api_response)
    )

    await web_search.run(WebSearchArgs(query="test"))

    request = route.calls[0].request
    assert request.headers.get("X-Subscription-Token") == "test-api-key"
    assert request.headers.get("Accept") == "application/json"


def test_get_call_display_basic():
    from kin_code.core.types import ToolCallEvent

    args = WebSearchArgs(query="python async")
    event = ToolCallEvent(
        tool_name="web_search",
        tool_call_id="123",
        args=args,
        tool_class=WebSearch,
    )

    display = WebSearch.get_call_display(event)

    assert "python async" in display.summary


def test_get_call_display_with_freshness():
    from kin_code.core.types import ToolCallEvent

    args = WebSearchArgs(query="news", freshness="pd")
    event = ToolCallEvent(
        tool_name="web_search",
        tool_call_id="123",
        args=args,
        tool_class=WebSearch,
    )

    display = WebSearch.get_call_display(event)

    assert "news" in display.summary
    assert "past day" in display.summary


def test_get_result_display():
    from kin_code.core.types import ToolResultEvent
    from kin_code.core.tools.builtins.web_search import WebSearchResultItem

    result = WebSearchResult(
        results=[
            WebSearchResultItem(title="Test", url="https://test.com", description="Desc")
        ],
        query="test query",
        total_count=1,
    )
    event = ToolResultEvent(
        tool_name="web_search",
        tool_call_id="123",
        result=result,
        error=None,
        skipped=False,
        skip_reason=None,
        tool_class=WebSearch,
    )

    display = WebSearch.get_result_display(event)

    assert display.success
    assert "1 result" in display.message


def test_get_status_text():
    assert WebSearch.get_status_text() == "Searching the web"
