# llama-index-readers-agentreader

LlamaIndex reader for [AgentReader](https://agentreader.xyz): turn web pages, JavaScript-rendered pages, RSS/Atom feeds and PDF URLs into clean, compact Markdown `Document`s for indexing and agents.

- Works **without an API key** on the free tier (5 reads/day per IP).
- For more, buy prepaid credits at <https://agentreader.xyz/buy> ($3 for 2,000 reads, $10 for 7,000) and set `AGENTREADER_API_KEY`.
- Failed reads (bot checks, paywalls, upstream errors) return an error and are not charged.

## Install

```bash
pip install llama-index-readers-agentreader
```

## Usage

```python
from llama_index.core import VectorStoreIndex
from llama_index.readers.agentreader import AgentReaderWebReader

reader = AgentReaderWebReader()  # reads AGENTREADER_API_KEY if set
docs = reader.load_data([
    "https://react.dev/learn",
    "https://arxiv.org/pdf/1706.03762",  # PDF URLs work too
])
index = VectorStoreIndex.from_documents(docs)
```

Options: `mode` (`auto`, `article`, `links`, `full`), `render` (`auto`, `never`, `always`), `extract` (e.g. `"title,author,date,price"`, returned in `metadata["fields"]`), `continue_on_failure`.

Metadata: `source` (final URL), `requested_url`, and when available `title`, `author`, `date`, `siteName`, `description`, `lang`, `contentType`, `pageType`, `wordCount`, `pages`, `fields`.

Errors raise `AgentReaderError` with `status`, `code` and `reason` (for example `402` when the free tier is used up, `502`/`bot_challenge` when a site blocks automated reads).

Docs: <https://agentreader.xyz/llms.txt> · Remote MCP server: `https://agentreader.xyz/mcp` · LangChain loader: `langchain-agentreader`.

MIT licensed.
