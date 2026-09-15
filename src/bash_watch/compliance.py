"""Monthly change detector for laws, terms pages, and robots.txt."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import httpx
import yaml


def digest(body: bytes) -> str:
    return hashlib.sha256(body).hexdigest()


def load_state(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def fetch(url: str, user_agent: str) -> bytes:
    request = Request(url, headers={"User-Agent": user_agent})
    with urlopen(request, timeout=30) as response:
        return response.read()


def discord_message(
    changed: list[tuple[str, str]],
    errors: list[tuple[str, str]],
    baseline: bool,
) -> str:
    lines = ["🏀 バッシュ情報システム：月次コンプライアンス確認"]
    if baseline:
        lines.append("初回の比較基準を作成しました。次回から変更を検知します。")
    elif changed:
        lines.append(
            "次のページに前回確認時から変更があります。"
            "自動取得禁止・利用条件・法改正の有無を人が確認してください。"
        )
        lines.extend(f"・{name}: {url}" for name, url in changed)
    else:
        lines.append("監視対象ページの内容変更は検知されませんでした。")
    if errors:
        lines.append(
            "取得できなかったページ"
            "（アクセス制限を回避せず、設定見直しが必要です）:"
        )
        lines.extend(f"・{name}: {url}" for name, url in errors)
    lines.append(
        "※変更検知は法的判断ではありません。"
        "規約本文と法令の内容を確認してください。"
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="config/compliance_urls.yml")
    parser.add_argument("--state", default="data/compliance_state.json")
    args = parser.parse_args()

    config = yaml.safe_load(Path(args.config).read_text(encoding="utf-8"))
    state_path = Path(args.state)
    previous = load_state(state_path)
    current: dict[str, str] = {}
    changed: list[tuple[str, str]] = []
    errors: list[tuple[str, str]] = []

    for target in config["targets"]:
        try:
            value = digest(fetch(target["url"], config["user_agent"]))
            current[target["url"]] = value
            if target["url"] in previous and previous[target["url"]] != value:
                changed.append((target["name"], target["url"]))
        except (HTTPError, URLError, TimeoutError) as exc:
            errors.append((target["name"], target["url"]))
            if target["url"] in previous:
                current[target["url"]] = previous[target["url"]]
            print(f"warning: {target['name']}: {exc}")

    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(
        json.dumps(current, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    webhook = os.getenv("DISCORD_WEBHOOK_URL")
    if webhook:
        message = discord_message(changed, errors, baseline=not previous)
        response = httpx.post(webhook, json={"content": message}, timeout=30)
        response.raise_for_status()
    else:
        print("DISCORD_WEBHOOK_URL is not set; result was not sent.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
