import type { PriceResult, Unit } from "./types";

export const money = (n: number) => `$${n.toFixed(2)}`;

/** "280 g", "7.5 g", "250 ml", "2 each"; "" when the recipe gave no amount. */
export function formatAmount(amount: number | null, unit: Unit | null): string {
  if (amount == null) return "";
  const n = Number.isInteger(amount) ? String(amount) : String(Number(amount.toFixed(2)));
  return unit ? `${n} ${unit}` : n;
}

/** Recompute each row's cost per serving for a different number of servings. */
export function withServings(result: PriceResult, servings: number): PriceResult {
  return {
    ...result,
    rows: result.rows.map((r) => ({ ...r, cost_per_serving: Math.round((r.total_cost / servings) * 100) / 100 })),
  };
}
