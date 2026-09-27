export type Unit = "g" | "ml" | "each";

export interface Ingredient {
  id: number;
  name: string;
  amount: number | null;
  unit: Unit | null;
  raw: string;
  alternatives: string[];
}

export interface ParsedRecipe {
  title: string;
  servings: { min: number | null; max: number | null };
  ingredients: Ingredient[];
}

export interface CostRow {
  ingredient: string;
  amount: number | null;
  unit: Unit | null;
  source: string;
  product_name: string | null;
  product_url: string | null;
  unit_price: number;
  cost_per_serving: number;
  total_cost: number;
  note: string;
}

export interface PriceResult {
  rows: CostRow[];
  total_cost: number;
}
