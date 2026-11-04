"""LangChain integration for AgentReader: web pages and PDFs to clean Markdown for LLMs."""
__version__ = "0.1.0"

from ._client import AgentReaderClient, AgentReaderError  # noqa: E402
from .document_loaders import AgentReaderLoader  # noqa: E402

__all__ = ["AgentReaderLoader", "AgentReaderClient", "AgentReaderError", "__version__"]
