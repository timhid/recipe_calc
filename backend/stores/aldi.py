"""Aldi Australia: parses the server-rendered search results page."""
from urllib.parse import quote

import requests
from bs4 import BeautifulSoup

from matching import comparison_price, pack_count, parse_measure, parse_price
from models import Product
from stores import BROWSER_HEADERS, TIMEOUT

BASE_URL = "https://www.aldi.com.au"
_session = requests.Session()
_session.headers.update(BROWSER_HEADERS)


def _text(tile, selector: str) -> str:
    el = tile.select_one(selector)
    return el.get_text(" ", strip=True) if el else ""


def parse_results(html: str) -> list[Product]:
    products = []
    for tile in BeautifulSoup(html, "html.parser").select(".product-tile"):
        name = _text(tile, ".product-tile__name")
        link = tile.select_one("a.product-tile__link")
        price = parse_price(_text(tile, ".base-price"))
        if not name or not link or price is None:
            continue

        size = _text(tile, ".product-tile__unit-of-measurement")
        cmp_text = _text(tile, ".product-tile__comparison-price")  # "($0.29 per 100 g)"
        cmp = None
        if " per " in cmp_text:
            cmp_amount, cmp_measure = cmp_text.split(" per ", 1)
            cmp = comparison_price(parse_price(cmp_amount), cmp_measure)
        if cmp is None and (measure := parse_measure(size)) and "per piece" not in size:
            cmp = (price / measure[0], measure[1]) if measure[0] else None

        products.append(Product(
            store="aldi",
            name=name,
            price=price,
            url=BASE_URL + link["href"],
            cmp_price=cmp[0] if cmp else None,
            cmp_unit=cmp[1] if cmp else None,
            pack_count=pack_count(name, size),
        ))
    return products


def search(term: str) -> list[Product]:
    resp = _session.get(f"{BASE_URL}/results?q={quote(term)}", timeout=TIMEOUT)
    resp.raise_for_status()
    return parse_results(resp.text)
