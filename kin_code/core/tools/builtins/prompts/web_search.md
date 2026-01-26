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
