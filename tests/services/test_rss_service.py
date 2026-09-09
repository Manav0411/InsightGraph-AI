"""services/rss_service.py — feed parsing, HTML strip, recency filter, per-feed cap."""
import datetime
import io

import pytest

from services import rss_service


def _rss(items_xml: str) -> bytes:
    return (
        "<?xml version='1.0'?><rss version='2.0'><channel>"
        f"{items_xml}"
        "</channel></rss>"
    ).encode()


def _item(title, link, desc, dt: datetime.datetime):
    pub = dt.strftime("%a, %d %b %Y %H:%M:%S +0000")
    return (
        f"<item><title>{title}</title><link>{link}</link>"
        f"<description><![CDATA[{desc}]]></description><pubDate>{pub}</pubDate></item>"
    )


@pytest.fixture
def single_feed(monkeypatch):
    monkeypatch.setattr(rss_service, "RSS_FEEDS", {"MyLab": "http://lab/feed"})
    monkeypatch.setattr(rss_service, "extract_og_image", lambda *_a, **_k: None)

    def _serve(xml_bytes):
        monkeypatch.setattr(
            rss_service.urllib.request, "urlopen", lambda *a, **k: io.BytesIO(xml_bytes)
        )

    return _serve


def test_parses_prefixes_and_strips_html(single_feed):
    now = datetime.datetime.now(datetime.timezone.utc)
    single_feed(_rss(_item("New Model", "http://lab/a", "<p>Bold <b>news</b></p>", now)))

    out = rss_service.fetch_rss_feeds()

    assert len(out) == 1
    assert out[0]["title"] == "[MyLab] New Model"
    assert out[0]["url"] == "http://lab/a"
    assert "<" not in out[0]["content"] and "news" in out[0]["content"]
    assert out[0]["source"] == "rss"


def test_drops_items_older_than_7_days(single_feed):
    now = datetime.datetime.now(datetime.timezone.utc)
    old = now - datetime.timedelta(days=30)
    single_feed(_rss(_item("Fresh", "http://lab/fresh", "x", now) + _item("Stale", "http://lab/stale", "x", old)))

    out = rss_service.fetch_rss_feeds()

    assert [a["url"] for a in out] == ["http://lab/fresh"]


def test_respects_max_per_feed(single_feed):
    now = datetime.datetime.now(datetime.timezone.utc)
    items = "".join(
        _item(f"t{i}", f"http://lab/{i}", "x", now - datetime.timedelta(hours=i)) for i in range(5)
    )
    single_feed(_rss(items))

    out = rss_service.fetch_rss_feeds(max_per_feed=2)

    assert len(out) == 2


def test_one_feed_failing_does_not_break_others(monkeypatch):
    monkeypatch.setattr(rss_service, "RSS_FEEDS", {"BadFeed": "http://bad", "GoodFeed": "http://good"})
    monkeypatch.setattr(rss_service, "extract_og_image", lambda *_a, **_k: None)
    now = datetime.datetime.now(datetime.timezone.utc)
    good_xml = _rss(_item("OK", "http://good/a", "x", now))

    def urlopen(req, timeout=None):
        url = req.full_url if hasattr(req, "full_url") else req.get_full_url()
        if "bad" in url:
            raise RuntimeError("429")
        return io.BytesIO(good_xml)

    monkeypatch.setattr(rss_service.urllib.request, "urlopen", urlopen)

    out = rss_service.fetch_rss_feeds()
    assert [a["title"] for a in out] == ["[GoodFeed] OK"]
