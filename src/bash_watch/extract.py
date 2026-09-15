from __future__ import annotations

import json
import re
from collections.abc import Iterable
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup

from .models import Item


def _nodes(value: object) -> Iterable[dict]:
    if isinstance(value, dict):
        yield value
        graph = value.get("@graph")
        if graph is not None:
            yield from _nodes(graph)
    elif isinstance(value, list):
        for entry in value:
            yield from _nodes(entry)


def _types(node: dict) -> set[str]:
    raw = node.get("@type", [])
    return {raw} if isinstance(raw, str) else set(raw or [])


def _offer(node: dict) -> dict:
    offers = node.get("offers") or {}
    if isinstance(offers, list):
        return offers[0] if offers and isinstance(offers[0], dict) else {}
    return offers if isinstance(offers, dict) else {}


def _image(node: dict) -> str | None:
    image = node.get("image")
    if isinstance(image, str):
        return image
    if isinstance(image, list) and image:
        first = image[0]
        return first if isinstance(first, str) else None
    if isinstance(image, dict):
        return image.get("url")
    return None


def extract_items(html: str, source: dict) -> list[Item]:
    """Extract products from JSON-LD, then fall back to configured links."""
    soup = BeautifulSoup(html, "html.parser")
    found: dict[str, Item] = {}
    base_url = source["url"]

    for script in soup.select('script[type="application/ld+json"]'):
        try:
            payload = json.loads(script.string or script.get_text())
        except (json.JSONDecodeError, TypeError):
            continue
        for node in _nodes(payload):
            if "Product" not in _types(node) or not node.get("name"):
                continue
            offer = _offer(node)
            url = node.get("url") or offer.get("url")
            if not url:
                continue
            price = offer.get("price")
            currency = offer.get("priceCurrency")
            price_text = f"{price} {currency}" if price and currency else str(price) if price else None
            item = Item(
                source=source["name"],
                title=" ".join(str(node["name"]).split()),
                url=urljoin(base_url, str(url)),
                price=price_text,
                availability=_short_availability(offer.get("availability")),
                image=_image(node),
            )
            found[item.key] = item

    if found:
        return sorted(found.values(), key=lambda item: item.url)

    selector = source.get("link_selector", "a[href]")
    include = re.compile(source.get("include_url_regex", r"."), re.IGNORECASE)
    exclude = re.compile(source.get("exclude_title_regex", r"$^"), re.IGNORECASE)
    same_host = source.get("same_host", True)
    base_host = urlparse(base_url).netloc
    for anchor in soup.select(selector):
        href = anchor.get("href")
        title = anchor.get("aria-label") or anchor.get_text(" ", strip=True)
        if not href or not title:
            continue
        url = urljoin(base_url, href)
        if same_host and urlparse(url).netloc != base_host:
            continue
        if not include.search(url) or exclude.search(title):
            continue
        item = Item(source=source["name"], title=" ".join(title.split()), url=url)
        found[item.key] = item
    return sorted(found.values(), key=lambda item: item.url)


def _short_availability(value: object) -> str | None:
    if not value:
        return None
    return str(value).rsplit("/", 1)[-1]

