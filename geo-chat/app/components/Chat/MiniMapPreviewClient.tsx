"use client";
import MapComponent from "../Map/MapComponent";

export default function MiniMapPreviewClient() {
    return (
        <div className="h-44 w-full overflow-hidden rounded-xl border border-neutral-800 pointer-events-none">
            <MapComponent
                interactive={false}
            />
        </div>
    );
}