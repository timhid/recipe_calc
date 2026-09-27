# Recipe Cost Calculator

Upload a recipe PDF (printed from a recipe website) and get the cost of each ingredient at the cheapest
per-g/ml product from Aldi, falling back to Woolworths, with a downloadable CSV.

- `backend/` — Flask API (Python 3.12): PDF text extraction, ingredient parsing, supermarket scraping, pricing
- `frontend/` — Next.js (TypeScript, Tailwind): upload → review ingredients → cost table + CSV download

## Run

```bash
# backend (port 5000)
python -m venv .venv && .venv/bin/pip install -r backend/requirements.txt
.venv/bin/flask --app backend/app run

# frontend (port 3000), in another terminal
cd frontend && npm install && npm run dev
```

Open http://localhost:3000. The frontend proxies `/api/*` to the backend (`BACKEND_URL`, default `http://127.0.0.1:5000`).

## Tests

```bash
cd backend
../.venv/bin/pytest          # offline, uses saved fixtures
../.venv/bin/pytest -m live  # hits the real Aldi / Woolworths sites to check the scrapers still work
```

## How it works

1. **Text extraction** — pypdfium2 pulls the text out of every page.
2. **Ingredient parsing** (`recipe_parser.py`) — the ingredient block runs from the first line starting with a
   quantity after the "Ingredients" heading to the first numbered method step. Note lines (starting with `,` or
   `(`) and section headings are dropped. Each line is parsed as `quantity [unit] name`:
   g/kg → g, ml/L → ml, 1 tsp = 5 g, 1 tbsp = 15 g, 1 cup = 250 ml, no unit → count ("each").
   Imperial amounts (oz, lb) are ignored; `280g / 9 oz` keeps the 280 g.
3. **Review** — the user can fix names/amounts/units, remove items, and choose the number of servings.
4. **Matching** (`matching.py`) — a product matches when it contains every meaningful word of the ingredient
   and the ingredient's main noun ends the product name ("Cage Eggs" matches eggs, "Egg Fried Rice" does not).
5. **Pricing** (`pricing.py`) — Aldi's search page is scraped first, then Woolworths' search API. The matching
   product with the lowest price per g / ml / item wins; nothing found → $0. Duplicate ingredients are summed.
   `total cost = amount × price per unit`, `cost per serving = total cost ÷ servings`.

Assumptions: 1 g = 1 ml when a product is priced by the other unit; count items sold by weight use a typical
weight (e.g. 58 g per egg); water is free.
