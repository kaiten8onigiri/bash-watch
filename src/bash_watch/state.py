from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from .models import Change, Item


def load(path: Path) -> dict[str, Item]:
    if not path.exists():
        return {}
    payload = json.loads(path.read_text(encoding="utf-8"))
    return {key: Item(**value) for key, value in payload.get("items", {}).items()}


def diff(previous: dict[str, Item], current: dict[str, Item]) -> list[Change]:
    changes: list[Change] = []
    for key, item in current.items():
        old = previous.get(key)
        if old is None:
            changes.append(Change("new", item))
        elif old.fingerprint != item.fingerprint:
            changes.append(Change("updated", item, old))
    return changes


def save(path: Path, items: dict[str, Item], checked_at: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "checked_at": checked_at,
        "items": {key: asdict(value) for key, value in sorted(items.items())},
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

