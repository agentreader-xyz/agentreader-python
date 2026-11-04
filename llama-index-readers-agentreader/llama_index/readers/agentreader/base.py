"""LlamaIndex reader backed by AgentReader (https://agentreader.xyz)."""
from __future__ import annotations

import logging
from typing import Any, Dict, Iterable, List, Optional, Union

from llama_index.core.readers.base import BaseReader
from llama_index.core.schema import Document

from ._client import AgentReaderClient

logger = logging.getLogger(__name__)

_META_KEYS = ("title", "author", "date", "siteName", "description", "lang", "contentType", "pageType", "wordCount")


def _metadata(url: str, body: Dict[str, Any]) -> Dict[str, Any]:
    md: Dict[str, Any] = {"source": body.get("url") or url, "requested_url": url}
    for k in _META_KEYS:
        if body.get(k) is not None:
            md[k] = body[k]
    meta = body.get("meta") or {}
    if meta.get("pages") is not None:
        md["pages"] = meta["pages"]
    if body.get("fields"):
        md["fields"] = body["fields"]
    return md


class AgentReaderWebReader(BaseReader):
    """Read web pages, JS-rendered pages, feeds and PDF URLs as clean Markdown via AgentReader.

    Works without a key on the free tier (5 reads/day per IP). Set ``AGENTREADER_API_KEY``
    (or pass ``api_key``) for prepaid credits from https://agentreader.xyz/buy.

    Args:
        api_key: AgentReader API key; defaults to the ``AGENTREADER_API_KEY`` env var.
        mode: ``auto`` (default), ``article``, ``links`` or ``full``.
        render: ``auto`` (default), ``never`` or ``always``.
        extract: Optional comma list of fields, returned in ``metadata["fields"]``.
        continue_on_failure: Log and skip failing URLs instead of raising.
    """

    def __init__(self, api_key: Optional[str] = None, mode: Optional[str] = None, render: Optional[str] = None,
                 extract: Optional[str] = None, continue_on_failure: bool = False, base_url: Optional[str] = None,
                 timeout: float = 90.0, client: Optional[AgentReaderClient] = None) -> None:
        self.mode, self.render, self.extract = mode, render, extract
        self.continue_on_failure = continue_on_failure
        from . import __version__
        self.client = client or AgentReaderClient(api_key=api_key, base_url=base_url, timeout=timeout,
                                                  user_agent=f"llama-index-readers-agentreader/{__version__}")

    def lazy_load_data(self, urls: Union[str, Iterable[str]], **kwargs: Any) -> Iterable[Document]:
        for url in [urls] if isinstance(urls, str) else urls:
            try:
                body = self.client.read(url, mode=self.mode, render=self.render, extract=self.extract)
            except Exception as e:  # noqa: BLE001
                if self.continue_on_failure:
                    logger.warning("AgentReader failed for %s: %s", url, e)
                    continue
                raise
            yield Document(text=body.get("markdown") or body.get("text") or "", metadata=_metadata(url, body),
                           id_=body.get("url") or url)

    def load_data(self, urls: Union[str, Iterable[str]], **kwargs: Any) -> List[Document]:
        return list(self.lazy_load_data(urls, **kwargs))
