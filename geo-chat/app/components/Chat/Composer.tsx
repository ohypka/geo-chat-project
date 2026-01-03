"use client";

import { useState } from "react";

export default function Composer({ onSend }: { onSend: (text: string) => void }) {
    const [text, setText] = useState("");

    function submit() {
        const trimmed = text.trim();
        if (!trimmed) return;
        onSend(trimmed);
        setText("");
    }

    return (
        <div className="flex items-end gap-2 rounded-2xl border border-neutral-800 bg-neutral-900 px-3 py-2">
      <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Napisz wiadomość…"
          rows={1}
          className="flex-1 resize-none bg-transparent text-sm outline-none placeholder:text-neutral-500"
          onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  submit();
              }
          }}
      />
            <button
                onClick={submit}
                className="rounded-xl bg-neutral-200 px-3 py-2 text-sm font-medium text-neutral-950 hover:bg-white transition"
            >
                Wyślij
            </button>
        </div>
    );
}
