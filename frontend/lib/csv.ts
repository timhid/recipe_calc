import { formatAmount } from "./format";
import type { PriceResult } from "./types";

const HEADERS = [
  "Ingredient",
  "Amount required",
  "Source",
  "Unit price",
  "Cost per serving",
  "Total cost",
  "Product name",
  "Product URL",
];

function cell(value: string | number | null | undefined): string {
  const s = value == null ? "" : String(value);
  return /[",\n\r]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s;
}

export function toCsv(result: PriceResult): string {
  const lines = [HEADERS.map(cell).join(",")];
  for (const r of result.rows) {
    lines.push(
      [
        r.ingredient,
        formatAmount(r.amount, r.unit),
        r.source,
        r.unit_price.toFixed(2),
        r.cost_per_serving.toFixed(2),
        r.total_cost.toFixed(2),
        r.product_name,
        r.product_url,
      ]
        .map(cell)
        .join(","),
    );
  }
  const total = ["TOTAL recipe cost", "", "", "", "", result.total_cost.toFixed(2), "", ""];
  lines.push(total.map(cell).join(","));
  return lines.join("\r\n") + "\r\n";
}

export function downloadCsv(filename: string, csv: string) {
  const blob = new Blob([csv], { type: "text/csv;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
}

export function csvFilename(title: string): string {
  const slug = title.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");
  return `${slug || "recipe"}-cost.csv`;
}
