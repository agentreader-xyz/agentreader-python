import os

import pytest

from langchain_agentreader import AgentReaderError, AgentReaderLoader


def test_free_tier_no_key(server):
    base, seen = server
    docs = AgentReaderLoader(["https://a.test/page", "https://a.test/doc.pdf"], base_url=base).load()
    assert len(docs) == 2
    assert docs[0].page_content.startswith("# T")
    assert docs[0].metadata["source"] == "https://a.test/page/final"
    assert docs[0].metadata["requested_url"] == "https://a.test/page"
    assert docs[0].metadata["title"] == "T" and "author" not in docs[0].metadata
    assert docs[0].metadata["agentreader_tier"] == "free-anon"
    assert docs[1].metadata["pages"] == 2 and docs[1].metadata["contentType"] == "pdf"
    assert seen[0]["path"] == "/v1/read" and seen[0]["q"]["format"] == ["json"]
    assert seen[0]["auth"] is None
    assert seen[0]["ua"].startswith("langchain-agentreader/")


def test_key_from_env_and_options(server, monkeypatch):
    base, seen = server
    monkeypatch.setenv("AGENTREADER_API_KEY", "ar_test")
    docs = AgentReaderLoader("https://a.test/p", base_url=base, mode="article", render="never", extract="price").load()
    assert seen[0]["auth"] == "Bearer ar_test"
    assert seen[0]["q"]["mode"] == ["article"] and seen[0]["q"]["render"] == ["never"]
    assert docs[0].metadata["fields"] == {"price": "9"}


def test_errors_raise_and_skip(server):
    base, _ = server
    with pytest.raises(AgentReaderError) as e:
        AgentReaderLoader("https://a.test/limit", base_url=base).load()
    assert e.value.status == 402 and "/buy" in str(e.value)
    with pytest.raises(AgentReaderError) as e:
        AgentReaderLoader("https://a.test/blocked", base_url=base).load()
    assert e.value.reason == "bot_challenge"
    docs = AgentReaderLoader(["https://a.test/blocked", "https://a.test/ok"], base_url=base, continue_on_failure=True).load()
    assert len(docs) == 1


@pytest.mark.skipif(not os.environ.get("AGENTREADER_LIVE"), reason="set AGENTREADER_LIVE=1 to hit the real API")
def test_live():
    docs = AgentReaderLoader("https://example.com").load()
    assert "Example Domain" in docs[0].page_content
