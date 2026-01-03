"use client";

type Thread = { id: string; title: string };

export default function Sidebar({
  open,
  setOpen,
  threads,
  activeThreadId,
  onSelectThread,
  onNewChat,
  onDeleteThread,
}: {
  open: boolean;
  setOpen: (v: boolean) => void;
  threads: Thread[];
  activeThreadId: string;
  onSelectThread: (id: string) => void;
  onNewChat: () => void;
  onDeleteThread: (id: string) => void;
}) {
  return (
    <aside
      className={[
        "h-full border-r border-neutral-800 bg-neutral-900/60 backdrop-blur",
        open ? "w-72" : "w-0",
        "transition-[width] duration-200 overflow-hidden",
      ].join(" ")}
    >
      <div className="flex h-full flex-col">
        <div className="flex items-center justify-between gap-2 p-3">
          <button
            onClick={onNewChat}
            className="w-full rounded-lg bg-neutral-800 hover:bg-neutral-700 px-3 py-2 text-sm font-medium transition"
          >
            + Nowy czat
          </button>

          <button
            onClick={() => setOpen(false)}
            className="rounded-lg px-2 py-2 hover:bg-neutral-800 transition"
            aria-label="Zamknij panel boczny"
            title="Zamknij"
          >
            ✕
          </button>
        </div>

        <div className="px-3 pb-2">
          <div className="text-xs uppercase tracking-wider text-neutral-400">
            Czaty
          </div>
        </div>

        <nav className="flex-1 overflow-y-auto px-2 pb-3">
          <ul className="space-y-1">
            {threads.map((t) => {
              const active = t.id === activeThreadId;

              return (
                <li key={t.id}>
                  <button
                    onClick={() => onSelectThread(t.id)}
                    className={[
                      "group w-full text-left rounded-lg px-3 py-2 text-sm transition flex items-center justify-between gap-2",
                      active ? "bg-neutral-800" : "hover:bg-neutral-800/70",
                    ].join(" ")}
                  >
                    <span className="truncate">{t.title}</span>

                    {active && (
                      <div
                        onClick={(e) => {
                          e.stopPropagation();
                          onDeleteThread(t.id);
                        }}
                        title="Usuń czat"
                        aria-label="Usuń czat"
                        role="button"
                        tabIndex={0}
                        onKeyDown={(e) => {
                          if (e.key === 'Enter' || e.key === ' ') {
                            e.preventDefault();
                            e.stopPropagation();
                            onDeleteThread(t.id);
                          }
                        }}
                        className="opacity-0 group-hover:opacity-100 inline-flex h-7 w-7 items-center justify-center rounded-md hover:bg-neutral-700 transition cursor-pointer"
                      >
                        <svg
                          xmlns="http://www.w3.org/2000/svg"
                          width="14"
                          height="14"
                          viewBox="0 0 24 24"
                          fill="none"
                          stroke="currentColor"
                          strokeWidth="2"
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          className="text-neutral-300"
                        >
                          <path d="M3 6h18" />
                          <path d="M8 6v12" />
                          <path d="M16 6v12" />
                          <path d="M5 6l1 14a2 2 0 0 0 2 2h8a2 2 0 0 0 2-2l1-14" />
                          <path d="M10 6V4a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1v2" />
                        </svg>
                      </div>
                    )}
                  </button>
                </li>
              );
            })}
          </ul>
        </nav>

        <div className="border-t border-neutral-800 p-3 text-xs text-neutral-400">
          Strona główna
        </div>
      </div>
    </aside>
  );
}
