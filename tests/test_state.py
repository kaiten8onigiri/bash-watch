from bash_watch.models import Item
from bash_watch.state import diff


def test_detects_new_and_updated_items():
    old = Item("Nike", "Shoe", "https://example.com/p/1", price="100 JPY")
    updated = Item("Nike", "Shoe", "https://example.com/p/1", price="200 JPY")
    new = Item("Nike", "New Shoe", "https://example.com/p/2")
    changes = diff({old.key: old}, {updated.key: updated, new.key: new})
    assert [(change.kind, change.item.title) for change in changes] == [
        ("updated", "Shoe"), ("new", "New Shoe")
    ]

