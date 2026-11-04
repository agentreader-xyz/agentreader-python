import pytest

from llama_index.core.readers.base import BaseReader
from llama_index.readers.agentreader import AgentReaderError, AgentReaderWebReader


def test_class():
    assert issubclass(AgentReaderWebReader, BaseReader)


def test_free_tier_and_metadata(server):
    base, seen = server
    docs = AgentReaderWebReader(base_url=base).load_data(["https://a.test/page", "https://a.test/doc.pdf"])
    assert len(docs) == 2 and docs[0].text.startswith("# T")
    assert docs[0].metadata["source"] == "https://a.test/page/final"
    assert docs[1].metadata["pages"] == 2
    assert seen[0]["auth"] is None and seen[0]["ua"].startswith("llama-index-readers-agentreader/")


def test_key_and_errors(server, monkeypatch):
    base, seen = server
    monkeypatch.setenv("AGENTREADER_API_KEY", "ar_x")
    AgentReaderWebReader(base_url=base, extract="price").load_data("https://a.test/p")
    assert seen[0]["auth"] == "Bearer ar_x" and seen[0]["q"]["extract"] == ["price"]
    with pytest.raises(AgentReaderError) as e:
        AgentReaderWebReader(base_url=base).load_data("https://a.test/limit")
    assert e.value.status == 402
    assert len(AgentReaderWebReader(base_url=base, continue_on_failure=True).load_data(["https://a.test/blocked", "https://a.test/x"])) == 1
