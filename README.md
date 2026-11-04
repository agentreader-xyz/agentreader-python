# AgentReader Python integrations

Framework integrations for [AgentReader](https://agentreader.xyz), a read API and remote MCP server that turns any URL (web pages, JavaScript-rendered pages, feeds, PDFs) into clean, compact Markdown or JSON for LLMs.

| Package | Framework | Class |
|---|---|---|
| [`langchain-agentreader`](./langchain-agentreader) | LangChain | `AgentReaderLoader` (document loader) |
| [`llama-index-readers-agentreader`](./llama-index-readers-agentreader) | LlamaIndex | `AgentReaderWebReader` (reader) |

Both work without an API key on the free tier (5 reads/day per IP). Set `AGENTREADER_API_KEY` for prepaid credits from <https://agentreader.xyz/buy>.

Until the packages are on PyPI, install from this repo:

```bash
pip install "git+https://github.com/agentreader-xyz/agentreader-python#subdirectory=langchain-agentreader"
pip install "git+https://github.com/agentreader-xyz/agentreader-python#subdirectory=llama-index-readers-agentreader"
```

API docs: <https://agentreader.xyz/llms.txt> · MCP: `https://agentreader.xyz/mcp` · Contact: contact@agentreader.xyz

MIT licensed.
