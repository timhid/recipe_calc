import type { Ingredient, ParsedRecipe, PriceResult } from "./types";

async function handle<T>(res: Response): Promise<T> {
  const body = await res.json().catch(() => null);
  if (!res.ok) {
    throw new Error(body?.error ?? `Request failed (${res.status}). Is the Flask backend running?`);
  }
  return body as T;
}

export async function parseRecipe(file: File): Promise<ParsedRecipe> {
  const form = new FormData();
  form.append("file", file);
  return handle(await fetch("/api/parse", { method: "POST", body: form }));
}

export async function priceRecipe(servings: number, ingredients: Ingredient[]): Promise<PriceResult> {
  return handle(
    await fetch("/api/price", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ servings, ingredients }),
    }),
  );
}
