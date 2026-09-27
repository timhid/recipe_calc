import json

import pytest

import pricing
from models import Ingredient
from stores import aldi, woolworths


@pytest.fixture
def offline_stores(fixture_path, monkeypatch):
    aldi_by_term = {
        "brown sugar": aldi.parse_results(fixture_path("aldi_brown_sugar.html").read_text()),
        "eggs": aldi.parse_results(fixture_path("aldi_eggs.html").read_text()),
    }
    ww_by_term = {
        "pitted dates": woolworths.parse_results(json.loads(fixture_path("ww_pitted_dates.json").read_text())),
        "eggs": woolworths.parse_results(json.loads(fixture_path("ww_eggs.json").read_text())),
    }
    stores = [("aldi", lambda t: aldi_by_term.get(t, [])), ("woolworths", lambda t: ww_by_term.get(t, []))]
    monkeypatch.setattr(pricing, "STORES", stores)
    monkeypatch.setattr(pricing.find_best, "__defaults__", (stores,))
    pricing._cache.clear()


def test_price_recipe(offline_stores):
    ings = [
        Ingredient("brown sugar", 40, "g", alternatives=["brown sugar"]),
        Ingredient("brown sugar", 200, "g", alternatives=["brown sugar"]),
        Ingredient("pitted dates", 280, "g", alternatives=["pitted dates"]),
        Ingredient("boiling water", 250, "ml", alternatives=["boiling water"]),
        Ingredient("unicorn dust", 5, "g", alternatives=["unicorn dust"]),
        Ingredient("Ice cream", None, None, alternatives=["Ice cream"]),
    ]
    result = pricing.price_recipe(ings, servings=8)
    rows = {r["ingredient"]: r for r in result["rows"]}

    sugar = rows["brown sugar"]
    assert sugar["amount"] == 240 and sugar["source"] == "aldi"
    assert sugar["product_name"] == "Brown Sugar 1kg"
    assert sugar["unit_price"] == 2.89
    assert sugar["total_cost"] == pytest.approx(0.70)  # 240 g * $0.0029/g
    assert sugar["cost_per_serving"] == pytest.approx(0.09)

    dates = rows["pitted dates"]  # not at Aldi in the fixtures -> Woolworths, cheapest per kg
    assert dates["source"] == "woolworths"
    assert dates["product_name"] == "Woolworths Pitted Dates"
    assert dates["total_cost"] == pytest.approx(1.68)  # 280 g * $6/kg

    assert rows["boiling water"]["source"] == "free"
    assert rows["unicorn dust"]["source"] == "not found" and rows["unicorn dust"]["total_cost"] == 0
    assert rows["Ice cream"]["total_cost"] == 0

    assert result["total_cost"] == pytest.approx(sum(r["total_cost"] for r in result["rows"]))


def test_eggs_priced_per_egg(offline_stores):
    result = pricing.price_recipe([Ingredient("eggs", 2, "each", alternatives=["eggs"])], servings=1)
    row = result["rows"][0]
    assert row["source"] == "aldi"
    # $7.39 / 18 = $0.41 per egg, just beating Cage Eggs 700g at 58 g/egg ($0.4118)
    assert row["product_name"] == "Barn Laid Eggs 18 Pack 900g"
    assert row["total_cost"] == pytest.approx(0.82)


def test_amount_without_unit_is_not_priced(offline_stores):
    row = pricing.price_recipe([Ingredient("brown sugar", 100, None, alternatives=["brown sugar"])], 1)["rows"][0]
    assert row["total_cost"] == 0 and "unit" in row["note"]
