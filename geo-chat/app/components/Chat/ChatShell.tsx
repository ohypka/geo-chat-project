"use client";

import { useMemo, useState } from "react";
import Sidebar from "./Sidebar";
import ChatWindow from "./ChatWindow";
import type { Msg, Thread } from "./types";

const initialThreads: Thread[] = [
    { id: "t1", title: "Mapa: pogoda + jakość powietrza" },
    { id: "t2", title: "Lekarze NFZ w okolicy" },
];

const initialMessagesByThread: Record<string, Msg[]> = {
    t1: [
        { id: "m1", role: "assistant", type: "text", content: "Cześć! Opisz, co chcesz zobaczyć na mapie." },
        { id: "m2", role: "user", type: "text", content: "Pokaż jakość powietrza w Warszawie." },
        { id: "m3", role: "assistant", type: "text", content: "Ok. (Później podepniemy backend i mapę)" },
    ],
    t2: [
        { id: "m1", role: "assistant", type: "text", content: "Jakiej specjalizacji szukasz?" },
        { id: "m2", role: "user", type: "text", content: "Kardiolog" },
        { id: "m3", role: "assistant", type: "text", content: "Ok. (Później podepniemy backend i mapę)" },
    ],
};

export default function ChatShell() {
    const [threads, setThreads] = useState<Thread[]>(initialThreads);
    const [activeThreadId, setActiveThreadId] = useState<string>(initialThreads[0]?.id ?? "");
    const [messagesByThread, setMessagesByThread] = useState<Record<string, Msg[]>>(initialMessagesByThread);
    const [sidebarOpen, setSidebarOpen] = useState(true);

    const activeMessages = useMemo(() => {
        return messagesByThread[activeThreadId] ?? [];
    }, [activeThreadId, messagesByThread]);

    function createNewChat() {
        const id = `t${Date.now()}`;
        const title = "Nowy czat";

        setThreads((prev) => [{ id, title }, ...prev]);
        setActiveThreadId(id);

        setMessagesByThread((prev) => ({
            ...prev,
            [id]: [{ id: `m${Date.now()}`, role: "assistant", type: "text", content: "Cześć! O czym dziś rozmawiamy?" }],
        }));
    }

    function deleteThread(threadId: string) {
        setThreads((prev) => prev.filter((t) => t.id !== threadId));

        setMessagesByThread((prev) => {
            const copy = { ...prev };
            delete copy[threadId];
            return copy;
        });

        if (activeThreadId === threadId) {
            const nextActive = threads.find((t) => t.id !== threadId)?.id ?? "";
            setActiveThreadId(nextActive);
        }
    }

    function renameThread(threadId: string, title: string) {
        setThreads((prev) => prev.map((t) => (t.id === threadId ? { ...t, title } : t)));
    }

    function sendMessage(text: string) {
        if (!activeThreadId) return;

        const userMsg: Msg = { id: `m${Date.now()}u`, role: "user", type: "text", content: text };

        const assistantText: Msg = {
            id: `m${Date.now()}a1`,
            role: "assistant",
            type: "text",
            content: "Ok - tutaj masz podgląd mapy. Kliknij, żeby otworzyć pełny widok.",
        };

        const assistantMap: Msg = {
            id: `m${Date.now()}a2`,
            role: "assistant",
            type: "map",
            title: "Mapa: podgląd",
            subtitle: "Kliknij, aby otworzyć pełnoekranowo",
        };

        setMessagesByThread((prev) => ({
            ...prev,
            [activeThreadId]: [...(prev[activeThreadId] ?? []), userMsg, assistantText, assistantMap],
        }));

        const activeThread = threads.find((t) => t.id === activeThreadId);
        if (activeThread && activeThread.title === "Nowy czat") {
            renameThread(activeThreadId, text.slice(0, 28) + (text.length > 28 ? "…" : ""));
        }
    }

    return (
        <div className="h-screen w-screen bg-neutral-950 text-neutral-100">
            <div className="flex h-full">
                <Sidebar
                    open={sidebarOpen}
                    setOpen={setSidebarOpen}
                    threads={threads}
                    activeThreadId={activeThreadId}
                    onSelectThread={setActiveThreadId}
                    onNewChat={createNewChat}
                    onDeleteThread={deleteThread}
                />

                <main className="flex-1 h-full">
                    <ChatWindow
                        sidebarOpen={sidebarOpen}
                        onToggleSidebar={() => setSidebarOpen((v) => !v)}
                        threadTitle={threads.find((t) => t.id === activeThreadId)?.title ?? "Czat"}
                        messages={activeMessages}
                        onSend={sendMessage}
                    />
                </main>
            </div>
        </div>
    );
}
