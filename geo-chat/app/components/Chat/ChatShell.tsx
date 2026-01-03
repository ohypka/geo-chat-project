"use client";

import { useMemo, useState } from "react";
import Sidebar from "./Sidebar";
import ChatWindow from "./ChatWindow";
import type { Msg, Thread } from "./types";
import {
  fetchEnvironmentData,
  fetchDoctorsCoordinates,
  type EnvironmentData,
  type DoctorsResponse,
} from "@/lib/api";

const initialThreads: Thread[] = [
    { id: "t1", title: "Mapa: pogoda + jakość powietrza" },
    { id: "t2", title: "Lekarze NFZ w okolicy" },
];

const initialMessagesByThread: Record<string, Msg[]> = {
    t1: [
        { id: "m1", role: "assistant", type: "text", content: "Cześć! Opisz, co chcesz zobaczyć na mapie." },
    ],
    t2: [
        { id: "m1", role: "assistant", type: "text", content: "Jakiej specjalizacji szukasz?" },
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

        const userMsg: Msg = { id: `m${Date.now()}u`, role: "user", type: "text", content: text };

        setMessagesByThread((prev) => ({
            ...prev,
            [activeThreadId]: [...(prev[activeThreadId] ?? []), userMsg],
        }));

        const loadingMsg: Msg = {
            id: `m${Date.now()}loading`,
            role: "assistant",
            type: "text",
            content: "Pobieram dane...",
        };
        setMessagesByThread((prev) => ({
            ...prev,
            [activeThreadId]: [...(prev[activeThreadId] ?? []), loadingMsg],
        }));

        const activeThread = threads.find((t) => t.id === activeThreadId);
        if (activeThread && activeThread.title === "Nowy czat") {
            renameThread(activeThreadId, text.slice(0, 28) + (text.length > 28 ? "…" : ""));
        }

        // Default location: Warsaw
        const defaultLat = 52.2297;
        const defaultLon = 21.0122;

        try {
            const textLower = text.toLowerCase();
            let responseText = "";
            let mapMsg: Msg | null = null;

            // Simple intent detection
            if (textLower.includes("pogoda") || textLower.includes("powietrz") || textLower.includes("jakość")) {
                // Fetch weather/environment data
                const envData = await fetchEnvironmentData(defaultLat, defaultLon, "Warsaw");
                
                if (!envData) {
                    responseText = "Przepraszam, dane pogodowe nie są obecnie dostępne. Aby włączyć funkcję pogody, skonfiguruj klucz API OpenWeatherMap w backendzie (zmienna środowiskowa OPENWEATHER_API_KEY).";
                } else {
                    const temp = envData.metrics?.temperature ?? 0;
                    const aqi = envData.metrics?.aqi ?? 0;
                    const pm25 = envData.metrics?.pm25 ?? 0;

                    responseText = `Pogoda w Warszawie:\n• Temperatura: ${temp}°C\n• Jakość powietrza (AQI): ${aqi}\n• PM2.5: ${pm25} μg/m³\n• Wilgotność: ${envData.metrics?.humidity ?? "-"}%\n• Ciśnienie: ${envData.metrics?.pressure ?? "-"} hPa`;

                    mapMsg = {
                        id: `m${Date.now()}a2`,
                        role: "assistant",
                        type: "map",
                        title: "Mapa: pogoda i jakość powietrza",
                        subtitle: "Kliknij, aby otworzyć pełnoekranowo",
                    };
                }
            } else if (textLower.includes("lekarz") || textLower.includes("kardiolog") || textLower.includes("doktor")) {
                let serviceName = "KARDIOLOG";
                if (textLower.includes("ortoped")) serviceName = "ORTOPEDIA";
                else if (textLower.includes("okulist")) serviceName = "OKULISTYKA";
                else if (textLower.includes("neurolog")) serviceName = "NEUROLOGIA";

                const doctorsData = await fetchDoctorsCoordinates(defaultLat, defaultLon, serviceName, false);
                
                const getDaysUntilAppointment = (queueDate: string): number | null => {
                    if (!queueDate) return null;
                    try {
                        const appointmentDate = new Date(queueDate);
                        const today = new Date();
                        today.setHours(0, 0, 0, 0);
                        appointmentDate.setHours(0, 0, 0, 0);
                        const diffTime = appointmentDate.getTime() - today.getTime();
                        const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
                        return diffDays;
                    } catch {
                        return null;
                    }
                };

                const validResults = doctorsData.results
                    .filter((doctor) => {
                        const daysUntil = getDaysUntilAppointment(doctor.queue_date);
                        return daysUntil !== null && daysUntil >= 0;
                    })
                    .sort((a, b) => {
                        const daysA = getDaysUntilAppointment(a.queue_date) ?? Infinity;
                        const daysB = getDaysUntilAppointment(b.queue_date) ?? Infinity;
                        return daysA - daysB;
                    });

                const count = validResults.length;
                const nearest = validResults[0];

                if (nearest) {
                    const daysUntil = getDaysUntilAppointment(nearest.queue_date);
                    let waitingText = "";
                    if (daysUntil === 0) {
                        waitingText = "DZISIAJ";
                    } else if (daysUntil === 1) {
                        waitingText = "1 dzień";
                    } else {
                        waitingText = `${daysUntil} dni`;
                    }

                    responseText = `Znaleziono ${count} placówek ${serviceName.toLowerCase()} w okolicy.\n\nNajbliższa:\n• ${nearest.place || nearest.provider}\n• Adres: ${nearest.address || "Brak"}\n• Telefon: ${nearest.phone || "Brak"}\n• Czas oczekiwania: ${waitingText}\n• Data kolejki: ${nearest.queue_date}`;
                } else {
                    responseText = `Nie znaleziono dostępnych terminów ${serviceName.toLowerCase()} w okolicy.`;
                }

                mapMsg = {
                    id: `m${Date.now()}a2`,
                    role: "assistant",
                    type: "map",
                    title: `Mapa: placówki ${serviceName.toLowerCase()}`,
                    subtitle: "Kliknij, aby otworzyć pełnoekranowo",
                };
            } else {
                // Generic response
                responseText = "Rozumiem. Oto podgląd mapy z dostępnymi danymi.";
                mapMsg = {
                    id: `m${Date.now()}a2`,
                    role: "assistant",
                    type: "map",
                    title: "Mapa: podgląd",
                    subtitle: "Kliknij, aby otworzyć pełnoekranowo",
                };
            }

            // Remove loading message and add response
            setMessagesByThread((prev) => {
                const messages = prev[activeThreadId] ?? [];
                const filtered = messages.filter((m) => m.id !== loadingMsg.id);
                const assistantText: Msg = {
                    id: `m${Date.now()}a1`,
                    role: "assistant",
                    type: "text",
                    content: responseText,
                };
                const newMessages = [...filtered, assistantText];
                if (mapMsg) {
                    newMessages.push(mapMsg);
                }
                return {
                    ...prev,
                    [activeThreadId]: newMessages,
                };
            });
        } catch (error) {
            // Remove loading message and add error
            setMessagesByThread((prev) => {
                const messages = prev[activeThreadId] ?? [];
                const filtered = messages.filter((m) => m.id !== loadingMsg.id);
                const errorMsg: Msg = {
                    id: `m${Date.now()}error`,
                    role: "assistant",
                    type: "text",
                    content: `Przepraszam, wystąpił błąd podczas pobierania danych: ${error instanceof Error ? error.message : "Nieznany błąd"}. Upewnij się, że serwer backendowy jest uruchomiony na http://localhost:8000`,
                };
                return {
                    ...prev,
                    [activeThreadId]: [...filtered, errorMsg],
                };
            });
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
