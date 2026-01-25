"use client";

import { useEffect, useRef, useContext } from "react";
import MessageBubble from "./MessageBubble";
import Composer from "./Composer";
import type { Msg } from "./types";
import ChatContext from "@/app/context/ChatContext";

export default function ChatWindow({
                                       sidebarOpen,
                                       onToggleSidebar,
                                       threadTitle,
                                       messages,
                                       onSend,
                                   }: {
    sidebarOpen: boolean;
    onToggleSidebar: () => void;
    threadTitle: string;
    messages: Msg[];
    onSend: (text: string) => void;
}) {
    const bottomRef = useRef<HTMLDivElement | null>(null);

    const context = useContext(ChatContext);
    const isLoading = context?.isLoading;

    useEffect(() => {
        bottomRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [messages.length, isLoading]);

    return (
        <div className="flex h-full flex-col">
            <header className="flex items-center justify-between gap-3 border-b border-neutral-800 bg-neutral-950/70 px-4 py-3 backdrop-blur">
                {/* LEFT */}
                <div className="flex items-center gap-3">
                    {!sidebarOpen && (
                        <button
                            onClick={onToggleSidebar}
                            className="rounded-lg px-2 py-2 hover:bg-neutral-800 transition"
                            aria-label="Otwórz panel boczny"
                            title="Menu"
                        >
                            ☰
                        </button>
                    )}

                    <div className="text-sm text-neutral-300">
                        <span className="font-medium text-neutral-100">{threadTitle}</span>
                    </div>
                </div>

                {/* RIGHT – map button */}
                <a
                    href="/map"
                    title="Otwórz mapę"
                    aria-label="Otwórz mapę"
                    className="inline-flex h-9 w-9 items-center justify-center rounded-lg hover:bg-neutral-800 transition"
                >
                    <svg
                        xmlns="http://www.w3.org/2000/svg"
                        width="18"
                        height="18"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        strokeWidth="2"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        className="text-neutral-200"
                    >
                        <polygon points="3 6 9 3 15 6 21 3 21 18 15 21 9 18 3 21 3 6" />
                        <line x1="9" y1="3" x2="9" y2="18" />
                        <line x1="15" y1="6" x2="15" y2="21" />
                    </svg>
                </a>
            </header>


            <div className="flex-1 overflow-y-auto px-4 py-6">
                <div className="mx-auto w-full max-w-3xl space-y-4">
                    {messages.map((m) => (
                        <MessageBubble key={m.id} message={m} />
                    ))}

                    {isLoading && (
                        <div className="flex items-center gap-2 p-3 text-sm text-neutral-400 animate-pulse">
                            <div className="flex space-x-1">
                                <div className="h-1.5 w-1.5 bg-neutral-500 rounded-full animate-bounce [animation-delay:-0.3s]"></div>
                                <div className="h-1.5 w-1.5 bg-neutral-500 rounded-full animate-bounce [animation-delay:-0.15s]"></div>
                                <div className="h-1.5 w-1.5 bg-neutral-500 rounded-full animate-bounce"></div>
                            </div>
                            <span>Geo Chat analizuje dane i przygotowuje odpowiedź...</span>
                        </div>
                    )}

                    <div ref={bottomRef} />
                </div>
            </div>

            <div className="border-t border-neutral-800 bg-neutral-950/70 backdrop-blur">
                <div className="mx-auto w-full max-w-3xl px-4 py-4">
                    <Composer onSend={onSend} />
                </div>
            </div>
        </div>
    );
}
