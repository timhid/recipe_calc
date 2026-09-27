"use client";

import { useState } from "react";
import ResultsView from "@/components/ResultsView";
import ReviewIngredients from "@/components/ReviewIngredients";
import UploadCard from "@/components/UploadCard";
import { parseRecipe, priceRecipe } from "@/lib/api";
import type { Ingredient, ParsedRecipe, PriceResult } from "@/lib/types";

type Step =
  | { name: "upload" }
  | { name: "review"; recipe: ParsedRecipe; servings?: number }
  | { name: "results"; recipe: ParsedRecipe; servings: number; result: PriceResult };

export default function Home() {
  const [step, setStep] = useState<Step>({ name: "upload" });
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function run(task: () => Promise<void>) {
    setBusy(true);
    setError(null);
    try {
      await task();
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setBusy(false);
    }
  }

  const handleFile = (file: File) =>
    run(async () => {
      if (!file.name.toLowerCase().endsWith(".pdf")) throw new Error("Please choose a .pdf file.");
      setStep({ name: "review", recipe: await parseRecipe(file) });
    });

  const handleCalculate = (recipe: ParsedRecipe, servings: number, ingredients: Ingredient[]) =>
    run(async () => {
      const result = await priceRecipe(servings, ingredients);
      // Keep the edited ingredients so "Edit ingredients" returns to them.
      setStep({ name: "results", recipe: { ...recipe, ingredients }, servings, result });
    });

  const reset = () => {
    setError(null);
    setStep({ name: "upload" });
  };

  return (
    <main className="mx-auto w-full max-w-4xl flex-1 px-4 py-10 sm:px-6">
      <header className="mb-8">
        <h1 className="text-3xl font-bold tracking-tight">Recipe Cost Calculator</h1>
        <p className="mt-1 text-stone-600">What does a recipe really cost at Aldi or Woolworths?</p>
      </header>

      {error && (
        <div role="alert" className="mb-6 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-red-800">
          {error}
        </div>
      )}

      {step.name === "upload" && <UploadCard busy={busy} onFile={handleFile} />}

      {step.name === "review" && (
        <ReviewIngredients
          recipe={step.recipe}
          initialServings={step.servings}
          busy={busy}
          onCalculate={(servings, ingredients) => handleCalculate(step.recipe, servings, ingredients)}
          onCancel={reset}
        />
      )}

      {step.name === "results" && (
        <ResultsView
          recipe={step.recipe}
          result={step.result}
          servings={step.servings}
          onServingsChange={(servings) => setStep({ ...step, servings })}
          onEdit={() => setStep({ name: "review", recipe: step.recipe, servings: step.servings })}
          onReset={reset}
        />
      )}
    </main>
  );
}
