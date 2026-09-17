from pathlib import Path

from bash_watch.models import Item
from bash_watch.state import diff, load, merge_seen, save


def test_only_never_seen_product_codes_are_new():
    old = Item("Nike", "Shoe", "https://www.nike.com/jp/t/old-slug/IM4136-405", price="100 JPY")
    renamed = Item("Nike", "Renamed", "https://www.nike.com/jp/t/new-slug/IM4136-405", price="200 JPY")
    new = Item("Nike", "New Shoe", "https://www.nike.com/jp/t/new/AB1234-001")
    changes = diff({old.key: old}, {renamed.key: renamed, new.key: new})
    assert [(change.kind, change.item.title) for change in changes] == [("new", "New Shoe")]


def test_seen_product_is_retained_when_temporarily_missing():
    seen = Item("Nike", "Shoe", "https://www.nike.com/jp/t/shoe/IM4136-405")
    history = merge_seen({seen.key: seen}, {})
    assert history == {seen.key: seen}
    assert diff(history, {seen.key: seen}) == []


def test_price_and_title_changes_do_not_change_history():
    seen = Item("Nike", "Old", "https://www.nike.com/jp/t/old/IM4136-405", price="100")
    changed = Item("Nike", "New", "https://www.nike.com/jp/t/new/IM4136-405", price="200")
    assert merge_seen({seen.key: seen}, {changed.key: changed}) == {seen.key: seen}


def test_old_url_based_state_keys_are_migrated(tmp_path: Path):
    item = Item("Nike", "Shoe", "https://www.nike.com/jp/t/shoe/IM4136-405")
    path = tmp_path / "state.json"
    save(path, {"obsolete-url-key": item}, "now")
    assert load(path) == {item.key: item}
