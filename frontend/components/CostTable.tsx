import { formatAmount, money } from "@/lib/format";
import type { PriceResult } from "@/lib/types";

const SOURCE_LABELS: Record<string, string> = { aldi: "Aldi", woolworths: "Woolworths", free: "—", "not found": "Not found" };

export default function CostTable({ result, servings }: { result: PriceResult; servings: number }) {
  return (
    <div className="overflow-x-auto">
      <table className="w-full min-w-[640px] text-sm">
        <thead>
          <tr className="border-b border-stone-200 text-left text-stone-500">
            <th className="py-2 pr-3 font-medium">Ingredient</th>
            <th className="py-2 pr-3 text-right font-medium">Amount required</th>
            <th className="py-2 pr-3 font-medium">Source</th>
            <th className="py-2 pr-3 text-right font-medium">Unit price</th>
            <th className="py-2 pr-3 text-right font-medium">Cost per serving</th>
            <th className="py-2 text-right font-medium">Total cost</th>
          </tr>
        </thead>
        <tbody>
          {result.rows.map((row, i) => {
            const muted = !row.product_url || row.total_cost === 0;
            return (
              <tr key={i} className={`border-b border-stone-100 ${muted ? "text-stone-400" : ""}`} title={row.note || undefined}>
                <td className="py-2 pr-3">
                  {row.product_url ? (
                    <a
                      href={row.product_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="font-medium text-emerald-700 underline decoration-emerald-300 underline-offset-2 hover:decoration-emerald-700"
                    >
                      {row.ingredient}
                    </a>
                  ) : (
                    <span className="font-medium">{row.ingredient}</span>
                  )}
                  {row.product_name && <div className="text-xs text-stone-500">{row.product_name}</div>}
                  {row.note && <div className="text-xs text-amber-700">{row.note}</div>}
                </td>
                <td className="py-2 pr-3 text-right tabular-nums">{formatAmount(row.amount, row.unit) || "—"}</td>
                <td className="py-2 pr-3">{SOURCE_LABELS[row.source] ?? row.source}</td>
                <td className="py-2 pr-3 text-right tabular-nums">{money(row.unit_price)}</td>
                <td className="py-2 pr-3 text-right tabular-nums">{money(row.cost_per_serving)}</td>
                <td className="py-2 text-right tabular-nums">{money(row.total_cost)}</td>
              </tr>
            );
          })}
        </tbody>
        <tfoot>
          <tr className="border-t-2 border-stone-300 font-semibold">
            <td className="py-3 pr-3">TOTAL recipe cost</td>
            <td colSpan={4} className="py-3 pr-3 text-right text-xs font-normal text-stone-500">
              {money(result.total_cost / servings)} per serving × {servings}
            </td>
            <td className="py-3 text-right tabular-nums">{money(result.total_cost)}</td>
          </tr>
        </tfoot>
      </table>
    </div>
  );
}
