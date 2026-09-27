"""Woolworths: uses the JSON search endpoint behind woolworths.com.au (needs session cookies)."""
import threading

import requests

from matching import comparison_price, pack_count
from models import Product
from stores import BROWSER_HEADERS, TIMEOUT

BASE_URL = "https://www.woolworths.com.au"
_session = requests.Session()
_session.headers.update({**BROWSER_HEADERS, "Accept": "application/json, text/plain, */*"})
_warm = False
_lock = threading.Lock()


def _ensure_cookies():
    global _warm
    with _lock:
        if not _warm:
            _session.get(BASE_URL + "/", timeout=TIMEOUT)
            _warm = True


def parse_results(data: dict) -> list[Product]:
    products = []
    for bundle in data.get("Products") or []:
        for p in bundle.get("Products") or []:
            if not p.get("IsAvailable", True) or p.get("Price") is None:
                continue
            cmp = comparison_price(p.get("CupPrice"), p.get("CupMeasure") or "")
            products.append(Product(
                store="woolworths",
                name=p["Name"],
                price=float(p["Price"]),
                url=f"{BASE_URL}/shop/productdetails/{p['Stockcode']}/{p['UrlFriendlyName']}",
                cmp_price=cmp[0] if cmp else None,
                cmp_unit=cmp[1] if cmp else None,
                pack_count=pack_count(p["Name"], p.get("PackageSize") or ""),
            ))
    return products


def search(term: str) -> list[Product]:
    _ensure_cookies()
    resp = _session.get(
        f"{BASE_URL}/apis/ui/Search/products",
        params={"searchTerm": term, "pageSize": 24},
        timeout=TIMEOUT,
    )
    resp.raise_for_status()
    return parse_results(resp.json())
