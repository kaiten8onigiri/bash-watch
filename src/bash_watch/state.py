from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from .models import Change, Item


def load(path: Path) -> dict[str, Item]:
    if not path.exists():
        return {}
    payload = json.loads(path.read_text(encoding="utf-8"))
    items = [Item(**value) for value in payload.get("items", {}).values()]
    # Recalculate keys so existing URL-based state is migrated automatically.
    return {item.key: item for item in items}


def diff(previous: dict[str, Item], current: dict[str, Item]) -> list[Change]:
    """Notify only for product identities that have never been observed before."""
    return [Change("new", item) for key, item in current.items() if key not in previous]


def merge_seen(previous: dict[str, Item], current: dict[str, Item]) -> dict[str, Item]:
    """Keep an append-only ledger; known-product metadata changes are ignored."""
    return current | previous


def save(path: Path, items: dict[str, Item], checked_at: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "checked_at": checked_at,
        "items": {key: asdict(value) for key, value in sorted(items.items())},
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
