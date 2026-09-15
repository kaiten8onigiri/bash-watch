import asyncio

import httpx

from bash_watch.cli import fetch


class FakeClient:
    async def get(self, url):
        return httpx.Response(
            200,
            content=b'<html><a href="/help">Help</a></html>',
            request=httpx.Request("GET", url),
        )


def test_zero_items_is_a_source_failure():
    source = {"name": "Official", "url": "https://example.com", "include_url_regex": "/p/"}
    _, items, error = asyncio.run(fetch(FakeClient(), source))
    assert items == []
    assert error == "extracted 0 items (minimum: 1)"
