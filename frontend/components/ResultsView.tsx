"use client";

import { useMemo, useState } from "react";
import CostTable from "@/components/CostTable";
import { csvFilename, downloadCsv, toCsv } from "@/lib/csv";
import { withServings } from "@/lib/format";
import type { ParsedRecipe, PriceResult } from "@/lib/types";

interface Props {
  recipe: ParsedRecipe;
  result: PriceResult;
  servings: number;
  onServingsChange: (servings: number) => void;
  onEdit: () => void;
  onReset: () => void;
}

const secondaryButton = "rounded-lg border border-stone-300 px-5 py-2.5 font-medium hover:bg-stone-50";

export default function ResultsView({ recipe, result, servings, onServingsChange, onEdit, onReset }: Props) {
  // Kept as text so the field can be cleared while typing; the table uses the last valid number.
  const [input, setInput] = useState(String(servings));
  const table = useMemo(() => withServings(result, servings), [result, servings]);
  const invalid = !(Number(input) > 0);

  return (
    <section className="rounded-2xl border border-stone-200 bg-white p-6 shadow-sm">
      <div className="mb-4 flex flex-wrap items-end justify-between gap-4">
        <div>
          <h2 className="text-xl font-semibold">{recipe.title}</h2>
          <p className="text-sm text-stone-600">Click an ingredient to open the product page</p>
        </div>
        <div className="flex flex-wrap items-end gap-3">
          <label className="text-sm">
            <span className="block font-medium">Servings</span>
            <input
              type="number"
              min={1}
              step={1}
              value={input}
              aria-invalid={invalid}
              onChange={(e) => {
                setInput(e.target.value);
                const n = Number(e.target.value);
                if (n > 0) onServingsChange(n);
              }}
              onBlur={() => invalid && setInput(String(servings))}
              className={`mt-1 w-24 rounded-md border bg-white px-2 py-2 focus:outline-none ${
                invalid ? "border-red-400" : "border-stone-300 focus:border-emerald-600"
              }`}
            />
          </label>
          <button
            type="button"
            onClick={() => downloadCsv(csvFilename(recipe.title), toCsv(table))}
            className="rounded-lg bg-emerald-700 px-5 py-2.5 font-medium text-white hover:bg-emerald-800"
          >
            Download table
          </button>
        </div>
      </div>
      <CostTable result={table} servings={servings} />
      <div className="mt-6 flex flex-wrap gap-3">
        <button type="button" onClick={onEdit} className={secondaryButton}>
          Edit ingredients
        </button>
        <button type="button" onClick={onReset} className={secondaryButton}>
          Upload another recipe
        </button>
      </div>
    </section>
  );
}
