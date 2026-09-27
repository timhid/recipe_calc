"""Price a list of ingredients: Aldi first, then Woolworths, else $0."""
import logging
import threading
import time
from concurrent.futures import ThreadPoolExecutor

from matching import is_free, matches, price_per_recipe_unit, tokens
from models import CostRow, Ingredient, Product
from stores import aldi, woolworths

log = logging.getLogger(__name__)

STORES = [("aldi", aldi.search), ("woolworths", woolworths.search)]
CACHE_TTL = 3600
_cache: dict[tuple[str, str], tuple[float, list[Product]]] = {}
_cache_lock = threading.Lock()


def _search(store: str, fn, term: str) -> list[Product]:
    key = (store, term.lower())
    with _cache_lock:
        hit = _cache.get(key)
        if hit and time.time() - hit[0] < CACHE_TTL:
            return hit[1]
    try:
        products = fn(term)
    except Exception as exc:  # network errors, blocking, markup changes
        log.warning("%s search for %r failed: %s", store, term, exc)
        return []
    with _cache_lock:
        _cache[key] = (time.time(), products)
    return products


def merge_duplicates(ingredients: list[Ingredient]) -> list[Ingredient]:
    """Sum ingredients that appear more than once (e.g. butter in the batter and the sauce)."""
    merged: dict[tuple, Ingredient] = {}
    for ing in ingredients:
        key = (frozenset(tokens(ing.name)), ing.unit)
        if key in merged and ing.amount is not None and merged[key].amount is not None:
            merged[key].amount = round(merged[key].amount + ing.amount, 3)
        elif key not in merged:
            merged[key] = Ingredient(ing.name, ing.amount, ing.unit, ing.raw, list(ing.alternatives))
    return list(merged.values())


def find_best(ing: Ingredient, stores=STORES) -> tuple[Product, float | None, str] | None:
    """Cheapest matching product per g/ml/each, from the first store that has a match."""
    terms = ing.alternatives or [ing.name]
    priceable = ing.unit is not None and ing.amount is not None
    for store, fn in stores:
        best = None
        for term in terms:
            for product in _search(store, fn, term):
                if not any(matches(t, product.name) for t in terms):
                    continue
                if priceable:
                    ppu = price_per_recipe_unit(product, ing.unit, ing.name)
                    if ppu is None:
                        continue
                    if best is None or ppu[0] < best[1]:
                        best = (product, ppu[0], ppu[1])
                else:
                    # No amount: pick the cheapest by comparison price, just to show a product link.
                    rank = product.cmp_price if product.cmp_price is not None else product.price
                    if best is None or rank < best[1]:
                        best = (product, rank, "")
            if best:
                break
        if best:
            product, ppu, note = best
            return product, (ppu if priceable else None), note
    return None


def price_ingredient(ing: Ingredient, servings: float) -> CostRow:
    row = dict(ingredient=ing.name, amount=ing.amount, unit=ing.unit)
    if is_free(ing.name):
        return CostRow(**row, source="free", product_name=None, product_url=None,
                       unit_price=0.0, cost_per_serving=0.0, total_cost=0.0, note="Free ingredient")

    found = find_best(ing)
    if not found:
        return CostRow(**row, source="not found", product_name=None, product_url=None,
                       unit_price=0.0, cost_per_serving=0.0, total_cost=0.0, note="No matching product found")

    product, ppu, note = found
    if ppu is None:
        total = 0.0
        note = ("No quantity in recipe - enter an amount to price it" if ing.amount is None
                else "Choose a unit (g, ml or each) to price it")
    else:
        total = ing.amount * ppu
    return CostRow(
        **row,
        source=product.store,
        product_name=product.name,
        product_url=product.url,
        unit_price=round(product.price, 2),
        cost_per_serving=round(total / servings, 2) if servings else round(total, 2),
        total_cost=round(total, 2),
        note=note,
    )


def price_recipe(ingredients: list[Ingredient], servings: float) -> dict:
    items = merge_duplicates(ingredients)
    with ThreadPoolExecutor(max_workers=4) as pool:
        rows = list(pool.map(lambda i: price_ingredient(i, servings), items))
    return {
        "rows": [r.to_dict() for r in rows],
        "total_cost": round(sum(r.total_cost for r in rows), 2),
    }
