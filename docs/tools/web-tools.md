# Web Tools

Tools for web access and searching.

## web_fetch

Fetch content from a URL.

### Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `url` | string | The URL to fetch |

### Example

```
> web_fetch(url="https://example.com/api/data")
```

### Features

- HTTP GET requests
- Returns page content
- Handles redirects

### Notes

- May not work with JavaScript-heavy sites
- Large responses may be truncated
- Respects robots.txt

## web_search

Search the web.

### Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `query` | string | Search query |

### Example

```
> web_search(query="Python asyncio tutorial")
```

### Features

- Web search results
- Returns titles, URLs, and snippets

### Notes

- Requires configured search provider
- Results are summaries, not full pages
- Use web_fetch for full content

## Permissions

```toml
[tools.web_fetch]
permission = "ask"

[tools.web_search]
permission = "ask"
```

## Use Cases

- Fetching documentation
- Checking API responses
- Research tasks
- Verifying information

## Related

- [Tools Overview](overview.md)
- [Tool Permissions](permissions.md)
