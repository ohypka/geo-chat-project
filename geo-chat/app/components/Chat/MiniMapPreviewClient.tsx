"use client";

import dynamic from "next/dynamic";
import "leaflet/dist/leaflet.css";

// dynamic() gubi typy propsów -> rzutujemy na any (standard w Next + react-leaflet)
const MapContainer = dynamic(
    () => import("react-leaflet").then((mod) => mod.MapContainer),
    { ssr: false }
) as any;

const TileLayer = dynamic(
    () => import("react-leaflet").then((mod) => mod.TileLayer),
    { ssr: false }
) as any;

export default function MiniMapPreviewClient() {
    const center: [number, number] = [52.2297, 21.0122];

    return (
        <div className="h-44 w-full overflow-hidden rounded-xl border border-neutral-800">
            <MapContainer
                center={center}
                zoom={12}
                style={{ height: "100%", width: "100%" }}
                zoomControl={false}
                attributionControl={false}
                dragging={false}
                scrollWheelZoom={false}
                doubleClickZoom={false}
                boxZoom={false}
                keyboard={false}
                touchZoom={false}
            >
                <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
            </MapContainer>
        </div>
    );
}
