"use client";

import Link from "next/link";
import MiniMapPreview from "./MiniMapPreview";
import type { Msg } from "./types";

export default function MessageBubble({ message }: { message: Msg }) {
    const isUser = message.role === "user";

    if (message.type === "map") {
        return (
            <div className={isUser ? "flex justify-end" : "flex justify-start"}>
                <Link
                    href="/map"
                    className={[
                        "block max-w-[85%] rounded-2xl border border-neutral-800 bg-neutral-900 px-4 py-3",
                        "hover:border-neutral-700 hover:bg-neutral-900/80 transition",
                    ].join(" ")}
                    title="Otwórz mapę"
                >
                    <MiniMapPreview title={message.title} subtitle={message.subtitle} />
                </Link>
            </div>
        );
    }

    return (
        <div className={isUser ? "flex justify-end" : "flex justify-start"}>
            <div
                className={[
                    "max-w-[85%] rounded-2xl px-4 py-3 text-sm leading-relaxed",
                    isUser
                        ? "bg-neutral-200 text-neutral-950"
                        : "bg-neutral-900 text-neutral-100 border border-neutral-800",
                ].join(" ")}
            >
                <div className="whitespace-pre-wrap">{message.content}</div>
            </div>
        </div>
    );
}
