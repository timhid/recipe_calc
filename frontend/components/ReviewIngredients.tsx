"use client";

import { useState } from "react";
import type { Ingredient, ParsedRecipe, Unit } from "@/lib/types";

interface Props {
  recipe: ParsedRecipe;
  initialServings?: number;
  busy: boolean;
  onCalculate: (servings: number, ingredients: Ingredient[]) => void;
  onCancel: () => void;
}

const inputClass =
  "w-full rounded-md border border-stone-300 bg-white px-2 py-1.5 focus:border-emerald-600 focus:outline-none";

export default function ReviewIngredients({ recipe, initialServings, busy, onCalculate, onCancel }: Props) {
  const [items, setItems] = useState<Ingredient[]>(recipe.ingredients);
  const [servings, setServings] = useState<string>(String(initialServings ?? recipe.servings.min ?? 1));

  const update = (id: number, patch: Partial<Ingredient>) =>
    setItems((prev) => prev.map((i) => (i.id === id ? { ...i, ...patch } : i)));

  const addRow = () =>
    setItems((prev) => [
      ...prev,
      { id: Math.max(-1, ...prev.map((i) => i.id)) + 1, name: "", amount: null, unit: "g", raw: "", alternatives: [] },
    ]);

  const servingsNum = Number(servings);
  const valid = servingsNum > 0 && items.some((i) => i.name.trim());
  const { min, max } = recipe.servings;

  return (
    <section className="rounded-2xl border border-stone-200 bg-white p-6 shadow-sm">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h2 className="text-xl font-semibold">{recipe.title}</h2>
          <p className="mt-1 text-sm text-stone-600">
            Check the ingredients we found. Fix any amounts, remove optional items, then calculate.
          </p>
        </div>
        <label className="text-sm">
          <span className="block font-medium">Servings</span>
          <input
            type="number"
            min={1}
            step={1}
            value={servings}
            onChange={(e) => setServings(e.target.value)}
            className={`${inputClass} mt-1 w-24`}
          />
          {min != null && max != null && min !== max && (
            <span className="mt-1 block text-xs text-stone-500">
              Recipe says {min}–{max}
            </span>
          )}
        </label>
      </div>

      <div className="mt-6 overflow-x-auto">
        <table className="w-full min-w-[560px] text-sm">
          <thead className="text-left text-stone-500">
            <tr>
              <th className="pb-2 font-medium">Ingredient</th>
              <th className="w-28 pb-2 font-medium">Amount</th>
              <th className="w-24 pb-2 font-medium">Unit</th>
              <th className="w-10 pb-2" />
            </tr>
          </thead>
          <tbody>
            {items.map((ing) => (
              <tr key={ing.id} className="border-t border-stone-100 align-top">
                <td className="py-2 pr-3">
                  <input
                    value={ing.name}
                    aria-label="Ingredient name"
                    onChange={(e) => update(ing.id, { name: e.target.value, alternatives: [e.target.value] })}
                    className={inputClass}
                  />
                  {ing.raw && <div className="mt-1 text-xs text-stone-400">{ing.raw}</div>}
                </td>
                <td className="py-2 pr-3">
                  <input
                    type="number"
                    min={0}
                    step="any"
                    aria-label="Amount"
                    placeholder="—"
                    value={ing.amount ?? ""}
                    onChange={(e) => update(ing.id, { amount: e.target.value === "" ? null : Number(e.target.value) })}
                    className={inputClass}
                  />
                </td>
                <td className="py-2 pr-3">
                  <select
                    aria-label="Unit"
                    value={ing.unit ?? ""}
                    onChange={(e) => update(ing.id, { unit: (e.target.value || null) as Unit | null })}
                    className={inputClass}
                  >
                    <option value="g">g</option>
                    <option value="ml">ml</option>
                    <option value="each">each</option>
                    <option value="">—</option>
                  </select>
                </td>
                <td className="py-2 text-right">
                  <button
                    type="button"
                    aria-label={`Remove ${ing.name}`}
                    onClick={() => setItems((prev) => prev.filter((i) => i.id !== ing.id))}
                    className="rounded-md px-2 py-1.5 text-stone-400 hover:bg-red-50 hover:text-red-700"
                  >
                    ✕
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <button type="button" onClick={addRow} className="mt-3 text-sm font-medium text-emerald-700 hover:underline">
        + Add ingredient
      </button>

      <div className="mt-6 flex flex-wrap gap-3">
        <button
          type="button"
          disabled={!valid || busy}
          onClick={() => onCalculate(servingsNum, items.filter((i) => i.name.trim()))}
          className="rounded-lg bg-emerald-700 px-6 py-3 font-medium text-white hover:bg-emerald-800 disabled:opacity-60"
        >
          {busy ? "Checking supermarket prices…" : "Calculate cost"}
        </button>
        <button
          type="button"
          disabled={busy}
          onClick={onCancel}
          className="rounded-lg border border-stone-300 px-6 py-3 font-medium hover:bg-stone-50 disabled:opacity-60"
        >
          Upload a different recipe
        </button>
      </div>
    </section>
  );
}
