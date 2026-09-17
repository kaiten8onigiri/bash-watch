from bash_watch.models import Item


def test_nike_slug_change_keeps_same_identity():
    before = Item("Nike JP", "Old", "https://www.nike.com/jp/t/old-name/IM4136-405?cid=x")
    after = Item("Nike JP", "New", "https://www.nike.com/jp/t/new-name/IM4136-405")
    assert before.product_id == "im4136-405"
    assert before.key == after.key


def test_html_product_code_is_used():
    item = Item("adidas JP", "Shoe", "https://www.adidas.jp/shoe/IE2696.html")
    assert item.product_id == "ie2696"
