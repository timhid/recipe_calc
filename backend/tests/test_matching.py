import json

import pytest

from matching import matches, pack_count, parse_measure, price_per_recipe_unit
from models import Product
from stores import aldi, woolworths


@pytest.mark.parametrize("ingredient, product, ok", [
    ("brown sugar", "Brown Sugar 1kg", True),
    ("brown sugar", "Brown Onions 1kg", False),
    ("brown sugar", "Instant Gravy Mix Brown Onion Flavoured 120g", False),
    ("pitted dates", "Macro Organic Dates", True),
    ("eggs", "Free Range Eggs 700g", True),
    ("bi carb soda", "McKenzie's Bi Carb Soda", True),
    ("bi carb soda", "Woolworths Essentials Bicarbonate Soda", False),
    ("unsalted butter", "Salted Butter 250g", False),
    ("eggs", "Barn Laid Eggs 18 Pack 900g", True),
    ("eggs", "Eggs Free Range 12 Pack", True),
    ("eggs", "Egg Fried Rice Pouch 250g", False),
    ("eggs", "Kinder Surprise Egg Original 20g", False),
    ("eggs", "Free Range Egg Pasta Linguine 375g", False),
    ("ice cream", "Ice Cream Cones 12 Pack", False),
    ("unsalted butter", "Butter Unsalted 250g", True),
])
def test_matches(ingredient, product, ok):
    assert matches(ingredient, product) is ok


def test_parse_measure():
    assert parse_measure("100 g") == (100, "g")
    assert parse_measure("1KG") == (1000, "g")
    assert parse_measure("1 L") == (1000, "ml")
    assert parse_measure("1,000 g") == (1000, "g")
    assert parse_measure("1EA") == (1, "each")


def test_pack_count():
    assert pack_count("Woolworths 12 Pack Extra Large Cage Free Eggs") == 12
    assert pack_count("Coke Zero Sugar 18x375ml") == 18
    assert pack_count("Cage Eggs 700g") is None


def test_aldi_parse(fixture_path):
    products = aldi.parse_results(fixture_path("aldi_brown_sugar.html").read_text())
    sugar = next(p for p in products if p.name == "Brown Sugar 1kg")
    assert sugar.price == 2.89
    assert sugar.cmp_unit == "g" and sugar.cmp_price == pytest.approx(0.0029)
    assert sugar.url == "https://www.aldi.com.au/product/white-mill-brown-sugar-1kg-000000000000566355"


def test_woolworths_parse(fixture_path):
    products = woolworths.parse_results(json.loads(fixture_path("ww_pitted_dates.json").read_text()))
    dates = products[0]
    assert dates.name == "Woolworths Pitted Dates"
    assert dates.cmp_unit == "g" and dates.cmp_price == pytest.approx(0.006)
    assert dates.url == "https://www.woolworths.com.au/shop/productdetails/18160/woolworths-pitted-dates"


def test_price_each_by_pack_and_by_typical_weight():
    dozen = Product("woolworths", "Woolworths 12 Pack Eggs", 6.0, "u", 0.0086, "g", 12)
    assert price_per_recipe_unit(dozen, "each", "eggs") == (0.5, "")
    by_weight = Product("aldi", "Cage Eggs 700g", 5.0, "u", 5.0 / 700, "g", None)
    ppu, note = price_per_recipe_unit(by_weight, "each", "eggs")
    assert ppu == pytest.approx(58 * 5.0 / 700) and "58 g" in note
