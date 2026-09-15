import json

from bash_watch.compliance import digest, discord_message, load_state


def test_digest_is_stable():
    assert digest(b"same") == digest(b"same")
    assert digest(b"same") != digest(b"different")


def test_load_state_handles_missing_and_existing_file(tmp_path):
    path = tmp_path / "state.json"
    assert load_state(path) == {}

    path.write_text(json.dumps({"https://example.com": "abc"}), encoding="utf-8")
    assert load_state(path) == {"https://example.com": "abc"}


def test_discord_message_reports_changes_and_errors():
    message = discord_message(
        [("利用規約", "https://example.com/terms")],
        [("robots.txt", "https://example.com/robots.txt")],
        baseline=False,
    )
    assert "変更があります" in message
    assert "https://example.com/terms" in message
    assert "取得できなかった" in message
    assert "法的判断ではありません" in message
