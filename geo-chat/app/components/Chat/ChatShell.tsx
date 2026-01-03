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

    async function sendMessage(text: string) {
        if (!activeThreadId) return;

        // 1. Tworzymy wiadomość użytkownika
        const userMsg: Msg = {
            id: `m${Date.now()}u`,
            role: "user",
            type: "text",
            content: text
        };

        const currentHistory = messagesByThread[activeThreadId] ?? [];

        // 2. Dodajemy ją natychmiast do widoku (żeby użytkownik widział co napisał)
        setMessagesByThread((prev) => ({
            ...prev,
            [activeThreadId]: [...(prev[activeThreadId] ?? []), userMsg],
        }));

        // 3. Aktualizujemy nazwę wątku (jeśli to nowy czat)
        const activeThread = threads.find((t) => t.id === activeThreadId);
        if (activeThread && activeThread.title === "Nowy czat") {
            renameThread(activeThreadId, text.slice(0, 28) + (text.length > 28 ? "…" : ""));
        }

        try {
            // 3. Przygotowujemy historię dla backendu
            // Mapujemy 'assistant' na 'model', bo tak wymaga Gemini
            const historyToSend = currentHistory.map(msg => ({
                role: msg.role === "assistant" ? "model" : "user",
                parts: [{ text: msg.content }]
            }));

            // 4. Wysyłamy wiadomość + HISTORIĘ
            const response = await fetch("http://localhost:8000/api/chat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    message: text,
                    history: historyToSend, // <--- NOWOŚĆ: Wysyłamy pamięć
                    lat: 52.2297,
                    lon: 21.0122,
                }),
            });

            if (!response.ok) throw new Error("Błąd sieci");

            const data = await response.json();

            // 5. Tworzymy wiadomość od asystenta na podstawie odpowiedzi z AI
            const assistantMsg: Msg = {
                id: `m${Date.now()}a`,
                role: "assistant",
                type: "text",
                content: data.response || "Brak odpowiedzi.",
            };

            // 6. Dodajemy odpowiedź AI do widoku
            setMessagesByThread((prev) => ({
                ...prev,
                [activeThreadId]: [...(prev[activeThreadId] ?? []), assistantMsg],
            }));

        } catch (error) {
            console.error(error);
            // Opcjonalnie: komunikat o błędzie
            const errorMsg: Msg = {
                id: `m${Date.now()}e`,
                role: "assistant",
                type: "text",
                content: "Nie udało się połączyć z serwerem."
            };
            setMessagesByThread((prev) => ({
                ...prev,
                [activeThreadId]: [...(prev[activeThreadId] ?? []), errorMsg],
            }));
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
