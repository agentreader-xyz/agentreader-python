"""LangChain document loader backed by AgentReader."""
from __future__ import annotations

import logging
from typing import Any, Dict, Iterator, List, Optional, Sequence, Union

from langchain_core.document_loaders import BaseLoader
from langchain_core.documents import Document

from ._client import AgentReaderClient

logger = logging.getLogger(__name__)

_META_KEYS = ("title", "author", "date", "siteName", "description", "lang", "contentType", "pageType", "wordCount")


def to_metadata(url: str, body: Dict[str, Any]) -> Dict[str, Any]:
    md: Dict[str, Any] = {"source": body.get("url") or url, "requested_url": url}
    for k in _META_KEYS:
        if body.get(k) is not None:
            md[k] = body[k]
    meta = body.get("meta") or {}
    if meta.get("pages") is not None:
        md["pages"] = meta["pages"]
    if meta.get("renderedWithBrowser") is not None:
        md["rendered_with_browser"] = meta["renderedWithBrowser"]
    if body.get("fields"):
        md["fields"] = body["fields"]
    usage = body.get("_usage") or {}
    if usage.get("tier"):
        md["agentreader_tier"] = usage["tier"]
    return md


class AgentReaderLoader(BaseLoader):
    """Load web pages and PDFs as clean Markdown via AgentReader (https://agentreader.xyz).

    Handles JavaScript-rendered pages, cookie walls and PDF URLs. Works without a key on the free
    tier (5 reads/day per IP); set ``AGENTREADER_API_KEY`` for prepaid credits.

    Example:
        .. code-block:: python

            from langchain_agentreader import AgentReaderLoader

            docs = AgentReaderLoader(["https://react.dev/learn"]).load()
            print(docs[0].page_content[:200], docs[0].metadata["title"])
    """

    def __init__(self, urls: Union[str, Sequence[str]], *, api_key: Optional[str] = None, mode: Optional[str] = None,
                 render: Optional[str] = None, extract: Optional[str] = None, continue_on_failure: bool = False,
                 base_url: Optional[str] = None, timeout: float = 90.0, client: Optional[AgentReaderClient] = None):
        """
        Args:
            urls: One URL or a list of URLs (web pages, RSS/Atom feeds or PDFs).
            api_key: AgentReader API key. Defaults to the ``AGENTREADER_API_KEY`` env var; omit for the free tier.
            mode: ``auto`` (default), ``article``, ``links`` or ``full``.
            render: ``auto`` (default), ``never`` or ``always`` (headless browser).
            extract: Optional comma list of fields (e.g. ``title,author,date,price``); returned in ``metadata["fields"]``.
            continue_on_failure: Log and skip URLs that fail instead of raising.
        """
        self.urls: List[str] = [urls] if isinstance(urls, str) else list(urls)
        self.mode, self.render, self.extract = mode, render, extract
        self.continue_on_failure = continue_on_failure
        from . import __version__
        self.client = client or AgentReaderClient(api_key=api_key, base_url=base_url, timeout=timeout,
                                                  user_agent=f"langchain-agentreader/{__version__}")

    def lazy_load(self) -> Iterator[Document]:
        for url in self.urls:
            try:
                body = self.client.read(url, mode=self.mode, render=self.render, extract=self.extract)
            except Exception as e:  # noqa: BLE001
                if self.continue_on_failure:
                    logger.warning("AgentReader failed for %s: %s", url, e)
                    continue
                raise
            yield Document(page_content=body.get("markdown") or body.get("text") or "", metadata=to_metadata(url, body))
