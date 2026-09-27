from flask import Flask, jsonify, request

from models import Ingredient
from pdf_text import extract_text
from pricing import price_recipe
from recipe_parser import parse_recipe

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024


def error(message: str, status: int = 400):
    return jsonify({"error": message}), status


@app.post("/api/parse")
def parse():
    file = request.files.get("file")
    if file is None:
        return error("No file uploaded.")
    data = file.read()
    if not data.startswith(b"%PDF"):
        return error("That file isn't a PDF.")
    try:
        text = extract_text(data)
    except Exception:
        return error("Couldn't read that PDF.")

    recipe = parse_recipe(text)
    if not recipe["ingredients"]:
        return error("No ingredients found in that PDF.")
    return jsonify({
        "title": recipe["title"],
        "servings": recipe["servings"],
        "ingredients": [{"id": i, **ing.to_dict()} for i, ing in enumerate(recipe["ingredients"])],
    })


@app.post("/api/price")
def price():
    body = request.get_json(silent=True) or {}
    try:
        servings = float(body.get("servings") or 1)
        ingredients = [
            Ingredient(
                name=str(i["name"]).strip(),
                amount=float(i["amount"]) if i.get("amount") not in (None, "") else None,
                unit=i.get("unit") or None,
                raw=i.get("raw", ""),
                alternatives=[a for a in i.get("alternatives") or [] if a] or [str(i["name"]).strip()],
            )
            for i in body.get("ingredients") or []
            if str(i.get("name", "")).strip()
        ]
    except (KeyError, TypeError, ValueError):
        return error("Invalid ingredient data.")
    if servings <= 0:
        return error("Servings must be greater than 0.")
    if not ingredients:
        return error("No ingredients to price.")
    return jsonify(price_recipe(ingredients, servings))


@app.errorhandler(413)
def too_large(_):
    return error("PDF is too large (max 10 MB).", 413)
