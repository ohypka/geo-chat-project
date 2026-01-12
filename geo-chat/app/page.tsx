"use client";

import dynamic from "next/dynamic";

const MapComponent = dynamic(() => import("./components/Map/MapComponent.js"), {
  ssr: false
});

export default function MapPage() {
  return <MapComponent />;
}
