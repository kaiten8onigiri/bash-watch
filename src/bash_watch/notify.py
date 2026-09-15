from __future__ import annotations

import os
import smtplib
from email.message import EmailMessage

import httpx

from .models import Change


def format_message(changes: list[Change]) -> str:
    lines = [f"🏀 バッシュ公式情報: {len(changes)}件の更新"]
    for change in changes[:20]:
        marker = "NEW" if change.kind == "new" else "更新"
        detail = " / ".join(x for x in (change.item.price, change.item.availability) if x)
        lines.append(f"\n[{marker}] {change.item.source}: {change.item.title}")
        if detail:
            lines.append(detail)
        lines.append(change.item.url)
    if len(changes) > 20:
        lines.append(f"\nほか {len(changes) - 20}件")
    return "\n".join(lines)


def send(changes: list[Change], timeout: float = 15.0) -> list[str]:
    if not changes:
        return []
    message = format_message(changes)
    sent: list[str] = []
    with httpx.Client(timeout=timeout) as client:
        if url := os.getenv("DISCORD_WEBHOOK_URL"):
            response = client.post(url, json={"content": message[:2000]})
            response.raise_for_status()
            sent.append("Discord")
        if url := os.getenv("SLACK_WEBHOOK_URL"):
            response = client.post(url, json={"text": message})
            response.raise_for_status()
            sent.append("Slack")
        if url := os.getenv("GENERIC_WEBHOOK_URL"):
            response = client.post(
                url,
                json={"event": "basketball_shoe_update", "text": message,
                      "changes": [_change_dict(c) for c in changes]},
            )
            response.raise_for_status()
            sent.append("Webhook")
    if os.getenv("SMTP_HOST") and os.getenv("EMAIL_TO"):
        _send_email(message)
        sent.append("Email")
    return sent


def _change_dict(change: Change) -> dict:
    return {
        "kind": change.kind,
        "source": change.item.source,
        "title": change.item.title,
        "url": change.item.url,
        "price": change.item.price,
        "availability": change.item.availability,
    }


def _send_email(body: str) -> None:
    msg = EmailMessage()
    msg["Subject"] = "🏀 バッシュ公式情報の更新"
    msg["From"] = os.getenv("EMAIL_FROM", os.getenv("SMTP_USER", "bash-watch@localhost"))
    msg["To"] = os.environ["EMAIL_TO"]
    msg.set_content(body)
    port = int(os.getenv("SMTP_PORT", "587"))
    with smtplib.SMTP(os.environ["SMTP_HOST"], port, timeout=20) as server:
        server.starttls()
        if user := os.getenv("SMTP_USER"):
            server.login(user, os.environ["SMTP_PASSWORD"])
        server.send_message(msg)
