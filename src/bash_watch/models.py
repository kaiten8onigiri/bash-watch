from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class Item:
    source: str
    title: str
    url: str
    price: str | None = None
    availability: str | None = None
    image: str | None = None

    @property
    def key(self) -> str:
        canonical = self.url.split("?")[0].rstrip("/") or self.url
        return hashlib.sha256(f"{self.source}\0{canonical}".encode()).hexdigest()[:24]

    @property
    def fingerprint(self) -> str:
        payload = json.dumps(asdict(self), ensure_ascii=False, sort_keys=True)
        return hashlib.sha256(payload.encode()).hexdigest()


@dataclass(frozen=True)
class Change:
    kind: str
    item: Item
    previous: Item | None = None
