"""Smoke tests against the real store websites: pytest -m live"""
import pytest

from matching import matches
from stores import aldi, woolworths

pytestmark = pytest.mark.live


def test_aldi_live():
    products = aldi.search("brown sugar")
    assert any(matches("brown sugar", p.name) and p.cmp_price for p in products)


def test_woolworths_live():
    products = woolworths.search("pitted dates")
    assert any(matches("pitted dates", p.name) and p.cmp_price for p in products)
