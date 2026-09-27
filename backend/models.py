from dataclasses import dataclass, field, asdict


@dataclass
class Ingredient:
    name: str
    amount: float | None  # in g, ml or count; None when the recipe gives no usable metric amount
    unit: str | None  # "g" | "ml" | "each" | None
    raw: str = ""
    alternatives: list[str] = field(default_factory=list)  # search terms, best first

    def to_dict(self):
        return asdict(self)


@dataclass
class Product:
    store: str  # "aldi" | "woolworths"
    name: str
    price: float  # shelf price of the package
    url: str
    cmp_price: float | None = None  # $ per 1 g / 1 ml / 1 each
    cmp_unit: str | None = None  # "g" | "ml" | "each"
    pack_count: int | None = None  # items in the package, e.g. 12 for a dozen eggs


@dataclass
class CostRow:
    ingredient: str
    amount: float | None
    unit: str | None
    source: str
    product_name: str | None
    product_url: str | None
    unit_price: float
    cost_per_serving: float
    total_cost: float
    note: str = ""

    def to_dict(self):
        return asdict(self)
