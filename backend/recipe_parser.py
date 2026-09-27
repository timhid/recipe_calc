"""Rule-based extraction of ingredients and servings from recipe text.

Tuned for WordPress Recipe Maker style print pages (e.g. recipetineats.com),
where pypdfium2 emits every ingredient on its own line, followed by note lines
that start with "," or "(", and the method as numbered steps ("1. ...").
"""
import re

from models import Ingredient

UNICODE_FRACTIONS = {"½": 0.5, "¼": 0.25, "¾": 0.75, "⅓": 1 / 3, "⅔": 2 / 3, "⅛": 0.125}
_UF = "".join(UNICODE_FRACTIONS)

QTY = rf"(?:\d+\s*[{_UF}]|\d+\s+\d+/\d+|\d+/\d+|\d+(?:\.\d+)?|[{_UF}])"

# unit alias -> (base unit, multiplier). tsp/tbsp are converted to grams as specified.
METRIC_UNITS = {
    "g": ("g", 1), "gram": ("g", 1), "grams": ("g", 1),
    "kg": ("g", 1000), "kilogram": ("g", 1000), "kilograms": ("g", 1000),
    "ml": ("ml", 1), "millilitre": ("ml", 1), "millilitres": ("ml", 1), "milliliter": ("ml", 1), "milliliters": ("ml", 1),
    "l": ("ml", 1000), "litre": ("ml", 1000), "litres": ("ml", 1000), "liter": ("ml", 1000), "liters": ("ml", 1000),
    "tsp": ("g", 5), "teaspoon": ("g", 5), "teaspoons": ("g", 5),
    "tbsp": ("g", 15), "tablespoon": ("g", 15), "tablespoons": ("g", 15),
    "cup": ("ml", 250), "cups": ("ml", 250),
}
IMPERIAL_UNITS = {"oz", "ounce", "ounces", "lb", "lbs", "pound", "pounds", "fl oz", "pint", "pints", "quart", "quarts"}

_UNIT_ALT = "|".join(sorted((re.escape(u) for u in [*METRIC_UNITS, *IMPERIAL_UNITS]), key=len, reverse=True))
LINE_RE = re.compile(
    rf"^(?P<qty>{QTY})(?:\s*(?:-|–|to)\s*{QTY})?\s*(?P<unit>{_UNIT_ALT})?(?![a-z])\.?\s*(?P<rest>.*)$",
    re.IGNORECASE,
)
# "/ 9 oz" or "/ 6 tbsp" alternative measurement directly after the first one
ALT_MEASURE_RE = re.compile(rf"^/\s*(?P<qty>{QTY})\s*(?P<unit>{_UNIT_ALT})(?![a-z])\.?\s*", re.IGNORECASE)

STEP_RE = re.compile(r"^\d+\.\s")
QTY_START_RE = re.compile(rf"^{QTY}")
END_HEADERS = {"instructions", "method", "directions", "notes", "nutrition"}
SERVINGS_RES = [
    re.compile(r"(\d+)\s*(?:-|–|to)\s*(\d+)\s*(?:people|servings|serves|serving|pieces|portions)\b", re.I),
    re.compile(r"(\d+)\s*(?:people|servings|serves|portions)\b", re.I),
    re.compile(r"\b(?:serves|servings|yield)\s*:?\s*(\d+)(?:\s*(?:-|–|to)\s*(\d+))?", re.I),
]


def parse_quantity(text: str) -> float:
    text = text.strip()
    for ch, val in UNICODE_FRACTIONS.items():
        if ch in text:
            whole = text.replace(ch, "").strip()
            return (float(whole) if whole else 0) + val
    if "/" in text:
        parts = text.split()
        whole = float(parts[0]) if len(parts) == 2 else 0
        num, den = parts[-1].split("/")
        return whole + float(num) / float(den)
    return float(text)


def _clean_name(rest: str) -> list[str]:
    """Strip notes and return the ingredient name alternatives, best first."""
    rest = re.sub(r"\([^)]*\)", "", rest)  # parentheticals
    rest = rest.split(",")[0]  # trailing prep notes
    rest = re.sub(r"^\s*of\s+", "", rest, flags=re.I)
    alternatives = re.split(r"\s+/\s+|\s+or\s+", rest, flags=re.I)
    return [a.strip(" .;:-") for a in alternatives if a.strip(" .;:-")]


def parse_ingredient_line(line: str) -> Ingredient:
    raw = line.strip()
    m = LINE_RE.match(raw)
    if not m:
        alts = _clean_name(raw)
        return Ingredient(name=alts[0] if alts else raw, amount=None, unit=None, raw=raw, alternatives=alts)

    qty, unit, rest = parse_quantity(m["qty"]), (m["unit"] or "").lower(), m["rest"]
    amount: float | None
    base: str | None

    if unit in IMPERIAL_UNITS:
        # Imperial first: use a metric alternative if one follows ("9 oz / 280g dates"), else disregard.
        alt = ALT_MEASURE_RE.match(rest)
        if alt and alt["unit"].lower() in METRIC_UNITS:
            base, mult = METRIC_UNITS[alt["unit"].lower()]
            amount = parse_quantity(alt["qty"]) * mult
        else:
            amount, base = None, None
        rest = rest[alt.end():] if alt else rest
    elif unit:
        base, mult = METRIC_UNITS[unit]
        amount = qty * mult
    else:
        base, amount = "each", qty

    # Drop the secondary measurement ("280g / 9 oz", "80g / 6 tbsp").
    while (alt := ALT_MEASURE_RE.match(rest)):
        rest = rest[alt.end():]

    alts = _clean_name(rest)
    name = alts[0] if alts else rest.strip()
    return Ingredient(name=name, amount=round(amount, 3) if amount is not None else None, unit=base, raw=raw, alternatives=alts)


def _lines(text: str) -> list[str]:
    return [ln.strip() for ln in text.splitlines() if ln.strip()]


def find_ingredient_lines(text: str) -> list[str]:
    lines = _lines(text)
    header = next((i for i, ln in enumerate(lines) if ln.lower().rstrip(":") == "ingredients"), -1)

    start = None
    for i in range(header + 1, len(lines)):
        ln = lines[i]
        if QTY_START_RE.match(ln) and not STEP_RE.match(ln):
            # Without an "Ingredients" header, require a recognisable unit to avoid e.g. "15 mins".
            if header >= 0 or (LINE_RE.match(ln) and LINE_RE.match(ln)["unit"]):
                start = i
                break
    if start is None:
        return []

    items: list[str] = []
    for ln in lines[start:]:
        low = ln.lower().rstrip(":")
        if STEP_RE.match(ln) or low in END_HEADERS:
            break
        if ln.endswith(":"):  # section header, e.g. "Butterscotch Sauce:"
            continue
        if ln[0] in ",(" and items:  # note belonging to the previous ingredient
            items[-1] += " " + ln
            continue
        items.append(ln)
    return items


def find_servings(text: str) -> tuple[int | None, int | None]:
    for rx in SERVINGS_RES:
        m = rx.search(text)
        if m:
            lo = int(m[1])
            hi = int(m[2]) if m.lastindex and m.lastindex >= 2 and m[2] else lo
            return lo, hi
    return None, None


def parse_recipe(text: str) -> dict:
    lines = _lines(text)
    lo, hi = find_servings(text)
    ingredients = [parse_ingredient_line(ln) for ln in find_ingredient_lines(text)]
    return {
        "title": lines[0] if lines else "Recipe",
        "servings": {"min": lo, "max": hi},
        "ingredients": ingredients,
    }
