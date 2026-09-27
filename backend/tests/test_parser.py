import pytest

from pdf_text import extract_text
from recipe_parser import parse_ingredient_line, parse_recipe


@pytest.fixture
def sticky(fixture_path):
    return parse_recipe(extract_text(fixture_path("sticky.pdf").read_bytes()))


def test_sticky_date_pudding(sticky):
    assert sticky["title"] == "Sticky Date Pudding"
    assert sticky["servings"] == {"min": 7, "max": 9}
    got = [(i.name, i.amount, i.unit) for i in sticky["ingredients"]]
    assert got == [
        ("pitted dates", 280, "g"),
        ("baking soda", 5, "g"),
        ("boiling water", 250, "ml"),
        ("brown sugar", 40, "g"),
        ("unsalted butter", 80, "g"),
        ("eggs", 2, "each"),
        ("plain flour", 185, "g"),
        ("baking powder", 7.5, "g"),
        ("brown sugar", 200, "g"),
        ("thickened cream", 375, "ml"),
        ("vanilla extract", 2.5, "g"),
        ("unsalted butter", 70, "g"),
        ("Ice cream", None, None),
    ]
    assert sticky["ingredients"][1].alternatives == ["baking soda", "bi carb soda"]


@pytest.mark.parametrize("line, expected", [
    ("1 kg potatoes, peeled", ("potatoes", 1000, "g")),
    ("1.5 L chicken stock", ("chicken stock", 1500, "ml")),
    ("1/2 cup milk", ("milk", 125, "ml")),
    ("1 1/2 tbsp olive oil", ("olive oil", 22.5, "g")),
    ("½ tsp salt", ("salt", 2.5, "g")),
    ("2-3 garlic cloves", ("garlic cloves", 2, "each")),
    ("9 oz / 280g dates", ("dates", 280, "g")),
    ("8 oz cheddar", ("cheddar", None, None)),
    ("2 large eggs", ("large eggs", 2, "each")),
    ("Salt and pepper", ("Salt and pepper", None, None)),
])
def test_parse_line(line, expected):
    ing = parse_ingredient_line(line)
    assert (ing.name, ing.amount, ing.unit) == expected
