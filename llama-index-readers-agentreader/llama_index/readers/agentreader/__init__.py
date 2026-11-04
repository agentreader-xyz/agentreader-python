"""LlamaIndex reader for AgentReader: web pages and PDFs to clean Markdown for LLMs."""
__version__ = "0.1.0"

from ._client import AgentReaderClient, AgentReaderError  # noqa: E402
from .base import AgentReaderWebReader  # noqa: E402

__all__ = ["AgentReaderWebReader", "AgentReaderClient", "AgentReaderError", "__version__"]
