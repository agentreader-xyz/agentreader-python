# langchain-agentreader

LangChain document loader for [AgentReader](https://agentreader.xyz): turn web pages, JavaScript-rendered pages, RSS/Atom feeds and PDF URLs into clean, compact Markdown for LLMs and RAG.

- Works **without an API key** on the free tier (5 reads/day per IP).
- For more, buy prepaid credits at <https://agentreader.xyz/buy> ($3 for 2,000 reads, $10 for 7,000) and set `AGENTREADER_API_KEY`.
- Failed reads (bot checks, paywalls, upstream errors) return an error and are not charged.

## Install

```bash
pip install langchain-agentreader
```

## Usage

```python
from langchain_agentreader import AgentReaderLoader

loader = AgentReaderLoader([
    "https://react.dev/learn",
    "https://arxiv.org/pdf/1706.03762",   # PDF URLs work too
])
docs = loader.load()
print(docs[0].metadata["title"])
print(docs[0].page_content[:500])
```

With a key (env var, recommended):

```bash
export AGENTREADER_API_KEY=ar_...
```

or `AgentReaderLoader(urls, api_key="ar_...")`.

### Options

| Argument | Values | Notes |
|---|---|---|
| `mode` | `auto` (default), `article`, `links`, `full` | `links` returns a headline/link list for index pages |
| `render` | `auto` (default), `never`, `always` | `always` forces a headless browser |
| `extract` | e.g. `"title,author,date,price"` | Extracted values land in `metadata["fields"]` |
| `continue_on_failure` | `False` (default) | Log and skip failing URLs instead of raising |

### Metadata

Each `Document` has `source` (final URL after redirects), `requested_url`, and when available `title`, `author`, `date`, `siteName`, `description`, `lang`, `contentType`, `pageType`, `wordCount`, `pages` (PDFs), `rendered_with_browser`, `fields`.

### Errors

`AgentReaderError` carries `status`, `code` and `reason` (for example `402` when the free tier is used up, `502` with `bot_challenge` when a site blocks automated reads).

## Links

- API docs: <https://agentreader.xyz/llms.txt>
- Remote MCP server: `https://agentreader.xyz/mcp`
- LlamaIndex reader: [`llama-index-readers-agentreader`](https://github.com/agentreader-xyz/agentreader-python)

MIT licensed.
