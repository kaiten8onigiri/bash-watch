from __future__ import annotations

import argparse
import asyncio
import sys
from datetime import UTC, datetime
from pathlib import Path

import httpx
import yaml

from .extract import extract_items
from .models import Item
from .notify import send
from .state import diff, load, merge_seen, save

USER_AGENT = "bash-watch/0.2 (+official basketball shoe release monitor)"


async def fetch(client: httpx.AsyncClient, source: dict) -> tuple[dict, list[Item], str | None]:
    try:
        response = await client.get(source["url"])
        response.raise_for_status()
        if response.charset_encoding:
            encoding = response.charset_encoding.lower()
            response.encoding = "cp932" if encoding in {"windows-31j", "ms932"} else encoding
        items = extract_items(response.text, source)
        minimum = int(source.get("minimum_items", 1))
        if len(items) < minimum:
            return source, [], f"extracted {len(items)} items (minimum: {minimum})"
        return source, items, None
    except Exception as exc:  # noqa: BLE001
        return source, [], f"{type(exc).__name__}: {exc}"


async def run(args: argparse.Namespace) -> int:
    config = yaml.safe_load(args.config.read_text(encoding="utf-8"))
    enabled = [source for source in config["sources"] if source.get("enabled", True)]
    headers = {"User-Agent": config.get("user_agent", USER_AGENT), "Accept-Language": "ja-JP,ja;q=0.9"}
    limits = httpx.Limits(max_connections=4, max_keepalive_connections=2)
    async with httpx.AsyncClient(headers=headers, timeout=args.timeout, follow_redirects=True, limits=limits) as client:
        results = await asyncio.gather(*(fetch(client, source) for source in enabled))

    current: dict[str, Item] = {}
    failures: list[str] = []
    successful_sources: set[str] = set()
    for source, items, error in results:
        if error:
            failures.append(f"{source['name']}: {error}")
            continue
        successful_sources.add(source["name"])
        current.update({item.key: item for item in items})
        print(f"{source['name']}: {len(items)} items")

    previous = load(args.state)
    changes = diff(previous, current)
    first_run = not previous
    history = merge_seen(previous, current)
    state_changed = previous != history
    if args.dry_run:
        print(f"dry-run: {len(changes)} new products; state not written")
    else:
        if state_changed:
            save(args.state, history, datetime.now(UTC).isoformat())
        else:
            print("no new products; state not written")
        if args.notify and changes and (not first_run or args.notify_initial):
            destinations = send(changes)
            print("notified: " + (", ".join(destinations) or "no destinations configured"))
        elif first_run and changes:
            print("baseline created; initial items were not notified")

    for failure in failures:
        print(f"warning: {failure}", file=sys.stderr)
    return 1 if enabled and not successful_sources else 0


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Monitor official basketball shoe pages")
    p.add_argument("--config", type=Path, default=Path("config/sources.yml"))
    p.add_argument("--state", type=Path, default=Path("data/state.json"))
    p.add_argument("--timeout", type=float, default=25.0)
    p.add_argument("--notify", action="store_true")
    p.add_argument("--notify-initial", action="store_true")
    p.add_argument("--dry-run", action="store_true")
    return p


def main() -> None:
    raise SystemExit(asyncio.run(run(parser().parse_args())))


if __name__ == "__main__":
    main()
