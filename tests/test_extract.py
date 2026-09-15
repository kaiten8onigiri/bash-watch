from pathlib import Path

from bash_watch.extract import extract_items


def test_extracts_json_ld_products():
    html = Path("tests/fixtures/products.html").read_text()
    items = extract_items(html, {"name": "Official", "url": "https://example.com/list"})
    assert [item.title for item in items] == ["Test Shoe One", "Test Shoe Two"]
    assert items[0].url == "https://example.com/p/one"
    assert items[0].price == "16500 JPY"
    assert items[0].availability == "InStock"


def test_falls_back_to_matching_links():
    html = '<a href="/pd/ABC.html"> Fresh Foam BB </a><a href="/help">Help</a>'
    items = extract_items(html, {
        "name": "NB", "url": "https://shop.example/men/", "include_url_regex": r"/pd/.*\.html"
    })
    assert len(items) == 1
    assert items[0].title == "Fresh Foam BB"

