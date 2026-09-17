from __future__ import annotations

import hashlib
import json
import re
from dataclasses import asdict, dataclass
from urllib.parse import unquote, urlsplit


_PRODUCT_CODE = re.compile(r"(?i)(?=[a-z0-9_-]*[a-z])(?=[a-z0-9_-]*\d)([a-z0-9_-]+)$")


@dataclass(frozen=True)
class Item:
    source: str
    title: str
    url: str
    price: str | None = None
    availability: str | None = None
    image: str | None = None

    @property
    def product_id(self) -> str:
        """Return a stable official product identifier when the URL contains one."""
        path = unquote(urlsplit(self.url).path).rstrip("/")
        last = path.rsplit("/", 1)[-1]
        if last.lower().endswith(".html"):
            last = last[:-5]
        match = _PRODUCT_CODE.fullmatch(last)
        if match:
            return match.group(1).lower()
        # Fallback for sites that do not expose a model code. Query parameters and
        # fragments are deliberately excluded so tracking changes do not create news.
        return path.lower() or self.url.split("?", 1)[0].lower()

    @property
    def key(self) -> str:
        return hashlib.sha256(f"{self.source}\0{self.product_id}".encode()).hexdigest()[:24]

    @property
    def fingerprint(self) -> str:
        payload = json.dumps(asdict(self), ensure_ascii=False, sort_keys=True)
        return hashlib.sha256(payload.encode()).hexdigest()


@dataclass(frozen=True)
class Change:
    kind: str
    item: Item
    previous: Item | None = None
