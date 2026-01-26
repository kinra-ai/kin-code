Use `web_search` to find information, documentation, or solutions on the web.

**What it returns:**
- Lightweight metadata: title, URL, and snippet for each result
- Does NOT return full page content

**When to use:**
- Searching for error messages or stack traces
- Finding API or library documentation
- Looking up recent information not in training data
- Researching solutions to programming problems

**When NOT to use:**
- When you need full page content (use `web_fetch` instead with a URL)
- For information you already have in the conversation context

**Parameters:**
- `query`: The search query (required)
- `count`: Number of results (1-20, default 10)
- `freshness`: Time filter - `pd` (past day), `pw` (past week), `pm` (past month), `py` (past year)

**Workflow:**
1. Use `web_search` to find relevant URLs
2. Use `web_fetch` with promising URLs to get full content

**Configuration:**

Requires a Brave Search API key. Get a free key at https://brave.com/search/api/ (2,000 queries/month).

Add to `~/.kin-code/.env` (global) or `./.kin-code/.env` (project):
```
BRAVE_SEARCH_API_KEY=your-api-key-here
```

Optional `config.toml` settings:
```toml
[tools.web_search]
api_key_env_var = "BRAVE_SEARCH_API_KEY"  # Custom env var name
default_count = 10                         # Default result count
max_snippet_length = 500                   # Max description length
safesearch = "moderate"                    # off, moderate, strict
```
