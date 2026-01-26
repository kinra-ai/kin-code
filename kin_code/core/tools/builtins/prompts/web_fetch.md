Use `web_fetch` to retrieve full content from a web page URL.

**What it returns:**
- Plain text content (HTML stripped)
- Page title (if available)
- Truncation status

**When to use:**
- After `web_search` to read content from promising result URLs
- When you have a specific URL and need its full content
- Reading documentation pages, articles, or reference material

**When NOT to use:**
- For searching - use `web_search` first to find relevant URLs
- For very large pages that exceed content limits (will be truncated)

**Parameters:**
- `url`: The URL to fetch (required, must start with http:// or https://)
- `max_length`: Maximum content length in characters (optional)

**Notes:**
- Returns plain text, not raw HTML
- Large pages are automatically truncated
- Follows redirects automatically
- Handles common content types (HTML, plain text)

**Configuration:**

Optional `config.toml` settings:
```toml
[tools.web_fetch]
timeout = 30.0              # Request timeout in seconds
max_content_chars = 50000   # Max content length to return
max_redirects = 5           # Maximum redirects to follow
```
