"use client";

import { useRef } from "react";

interface Props {
  busy: boolean;
  onFile: (file: File) => void;
}

export default function UploadCard({ busy, onFile }: Props) {
  const input = useRef<HTMLInputElement>(null);

  return (
    <section className="rounded-2xl border border-stone-200 bg-white p-10 text-center shadow-sm">
      <h2 className="text-xl font-semibold">Upload a recipe</h2>
      <p className="mx-auto mt-2 max-w-md text-stone-600">
        Print a recipe from your favourite recipe website to PDF, then upload it here. We&apos;ll
        find each ingredient at Aldi or Woolworths and work out what it costs.
      </p>
      <input
        ref={input}
        type="file"
        accept="application/pdf,.pdf"
        className="hidden"
        onChange={(e) => {
          const file = e.target.files?.[0];
          e.target.value = "";
          if (file) onFile(file);
        }}
      />
      <button
        type="button"
        disabled={busy}
        onClick={() => input.current?.click()}
        className="mt-6 rounded-lg bg-emerald-700 px-6 py-3 font-medium text-white hover:bg-emerald-800 disabled:opacity-60"
      >
        {busy ? "Reading PDF…" : "Upload recipe PDF"}
      </button>
    </section>
  );
}
