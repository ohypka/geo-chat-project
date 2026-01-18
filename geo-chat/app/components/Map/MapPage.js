"use client";

import dynamic from "next/dynamic";

const MapComponent = dynamic(() => import("./MapComponent"), {
  ssr: false
});

export default function MapPage({mapData, layerType}) {
  return <MapComponent mapData={mapData} layerType={layerType}/>;
}
