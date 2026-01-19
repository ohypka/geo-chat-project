"use client";

import dynamic from "next/dynamic";

const MiniMapClient = dynamic(() => import("./MiniMapPreviewClient"), { ssr: false });

export default function MiniMapPreview({title = "Podgląd mapy", subtitle = "Kliknij, aby otworzyć pełny widok", mapData, layerType,}:
{title?: string; subtitle?: string; mapData: any; layerType?: string; }) {
    return (
        <div className="w-full">
            <div className="mb-2">
                <div className="text-sm font-medium text-neutral-100">{title}</div>
                <div className="text-xs text-neutral-400">{subtitle}</div>
            </div>
            <MiniMapClient mapData={mapData} layerType={layerType}/>
        </div>
    );
}
