"""Product relevance filtering and price normalisation."""
import re

from models import Product

# Descriptive words that don't change which product to buy.
STOPWORDS = {
    "a", "an", "the", "of", "and", "with", "for", "to", "in",
    "pitted", "chopped", "roughly", "finely", "diced", "sliced", "minced", "grated", "softened",
    "melted", "loosely", "tightly", "packed", "room", "temperature", "fresh", "freshly", "large",
    "small", "medium", "extra", "boiling", "hot", "cold", "warm", "cooled", "sifted", "beaten",
    "lightly", "optional", "ground", "whole", "organic", "pack", "pk",
}
# Words that may follow the head noun in a product name without changing what it is.
TRAILING_QUALIFIERS = {
    "free", "range", "cage", "barn", "laid", "natural", "pure", "australian", "light", "lite",
    "reduced", "fat", "salted", "unsalted", "plain", "white", "brown", "block", "bag", "tub",
    "bottle", "jar", "punnet", "loose", "each", "value",
}
# Ingredients that cost nothing.
FREE_INGREDIENTS = {"water", "tap water", "ice", "ice cubes"}
# Typical weight in grams of one item, used when a count ingredient is only sold by weight.
TYPICAL_ITEM_GRAMS = {"egg": 58, "onion": 180, "lemon": 120, "lime": 70, "garlic clove": 5, "clove": 5, "banana": 120, "apple": 180}

_SIZE_TOKEN = re.compile(r"^\d+(?:\.\d+)?(?:g|kg|ml|l|pk|pack|x)?$")


def _stem(token: str) -> str:
    if len(token) > 4 and token.endswith("ies"):
        return token[:-3] + "y"
    if len(token) > 3 and token.endswith("es") and token[-3] in "sxz":
        return token[:-2]
    if len(token) > 3 and token.endswith("s") and not token.endswith("ss"):
        return token[:-1]
    return token


def token_list(text: str) -> list[str]:
    words = re.findall(r"[a-z0-9.]+", text.lower().replace("-", " ").replace("bi carb", "bicarb"))
    return [_stem(w) for w in words if w not in STOPWORDS and not _SIZE_TOKEN.match(w)]


def tokens(text: str) -> set[str]:
    return set(token_list(text))


def matches(ingredient_name: str, product_name: str) -> bool:
    """True when the product is the ingredient itself, not something made from it.

    Every meaningful word of the ingredient must appear in the product name, and the
    ingredient's head noun (its last word) must end the product name, apart from
    trailing qualifiers: "Cage Eggs" and "Eggs Free Range" match "eggs", while
    "Egg Fried Rice" and "Kinder Surprise Egg Original" do not.
    """
    need = token_list(ingredient_name)
    have = token_list(product_name)
    if not need or not set(need) <= set(have):
        return False
    head = need[-1]
    after_head = have[len(have) - 1 - have[::-1].index(head) + 1:]
    return all(t in need or t in TRAILING_QUALIFIERS for t in after_head)


def is_free(name: str) -> bool:
    return " ".join(sorted(tokens(name))) in {" ".join(sorted(tokens(f))) for f in FREE_INGREDIENTS}


def typical_item_grams(name: str) -> float | None:
    toks = tokens(name)
    for key, grams in TYPICAL_ITEM_GRAMS.items():
        if tokens(key) <= toks:
            return grams
    return None


_MEASURE_RE = re.compile(r"([\d.,]+)\s*(kg|g|ml|l|ea|each|piece|pc)\b", re.I)
_UNIT_BASE = {"kg": ("g", 1000), "g": ("g", 1), "ml": ("ml", 1), "l": ("ml", 1000),
              "ea": ("each", 1), "each": ("each", 1), "piece": ("each", 1), "pc": ("each", 1)}


def parse_measure(text: str) -> tuple[float, str] | None:
    """'100 g' -> (100, 'g'); '1KG' -> (1000, 'g'); '1 L' -> (1000, 'ml'); '1EA' -> (1, 'each')."""
    m = _MEASURE_RE.search(text or "")
    if not m:
        return None
    base, mult = _UNIT_BASE[m[2].lower()]
    return float(m[1].replace(",", "")) * mult, base


def parse_price(text: str) -> float | None:
    m = re.search(r"\$\s*([\d,]+(?:\.\d+)?)", text or "")
    return float(m[1].replace(",", "")) if m else None


def comparison_price(price: float | None, measure_text: str) -> tuple[float, str] | None:
    """Price for a measure (e.g. $0.29 per '100 g') -> ($ per 1 base unit, base unit)."""
    measure = parse_measure(measure_text)
    if price is None or not measure or measure[0] == 0:
        return None
    return price / measure[0], measure[1]


_PACK_RES = [
    re.compile(r"(\d+)\s*(?:pack|pk)\b", re.I),
    re.compile(r"\b(\d+)\s*x\s*\d", re.I),
    re.compile(r"\bx\s*(\d+)\b", re.I),
    re.compile(r"^(?:\D+\s)?(\d+)\s+(?:\w+\s+){0,3}eggs\b", re.I),
]


def pack_count(*texts: str) -> int | None:
    for text in texts:
        for rx in _PACK_RES:
            if text and (m := rx.search(text)):
                n = int(m[1])
                if n > 1:
                    return n
    return None


def price_per_recipe_unit(product: Product, unit: str, ingredient_name: str) -> tuple[float, str] | None:
    """$ per 1 g/ml/each of the recipe unit for this product, plus a note on any assumption made."""
    if unit in ("g", "ml"):
        if product.cmp_unit == unit:
            return product.cmp_price, ""
        if product.cmp_unit in ("g", "ml"):
            return product.cmp_price, "assumed 1 g = 1 ml"
        return None
    if unit == "each":
        if product.pack_count:
            return product.price / product.pack_count, ""
        if product.cmp_unit == "each":
            return product.cmp_price, ""
        grams = typical_item_grams(ingredient_name)
        if grams and product.cmp_unit in ("g", "ml"):
            return product.cmp_price * grams, f"assumed {grams:g} g each"
    return None
