"use client";

import { useState, useEffect } from "react";
import { MapContainer, TileLayer, LayersControl, LayerGroup, Polyline, CircleMarker } from "react-leaflet";
import MarkerClusterGroup from 'react-leaflet-markercluster';
import MapMarker from "../markers/DoctorMarker.js";
import "leaflet/dist/leaflet.css";

const { Overlay } = LayersControl;

export default function MapComponent({mapData, layerType,interactive=true}) {
    const [isClient, setIsClient] = useState(false);

    useEffect(() => setIsClient(true), []);
    if (!isClient) return null;

    const features = mapData?.features || [];
    const type = layerType?.toLowerCase();

    const center = mapData.center ? [mapData.center[0], mapData.center[1]] : [52.2297, 21.0122];

  return (
      <MapContainer
          center={center}
          zoom={type==="traffic"?15:12}
          style={{ width: "100%", height: "100%" }}
          zoomControl={interactive}
          attributionControl={interactive}
          dragging={interactive}
          scrollWheelZoom={interactive}
          doubleClickZoom={interactive}
          boxZoom={interactive}
          keyboard={interactive}
          touchZoom={interactive}
      >
        <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />

        <LayersControl position="topright">

          <Overlay name="Doctors" checked={type === "doctors"}>
            <LayerGroup>
              <MarkerClusterGroup>
                {type === "doctors" && features.map((doc, i) => (
                    <MapMarker key={`doc-${i}`} marker={doc} />
                ))}
              </MarkerClusterGroup>
            </LayerGroup>
          </Overlay>

          <Overlay name="Weather" checked={type === "weather"}>
            <LayerGroup>
              {type === "weather" && features.map((feature, i) => {
                const marker = { ...feature, properties: { ...feature.properties, type: "weather" }};
                return <MapMarker key={`weather-${i}`} marker={marker} />;
              })}
            </LayerGroup>
          </Overlay>

          <Overlay name="Bikes" checked={type === "bikes"}>
            <LayerGroup>
                <MarkerClusterGroup>
                    {type === "bikes" && features.map((bike, i) => {
                        const marker={...bike, properties:{...bike.properties, type:"bike"}};
                        return <MapMarker key={`bike-${i}`} marker={marker} />;
                    })}
                </MarkerClusterGroup>

            </LayerGroup>
          </Overlay>

          <Overlay name="Traffic" checked={type === "traffic"}>
            <LayerGroup>
              {type === "traffic" && features.map((feature, i) => {
                const { coordinates } = feature.geometry;
                const props = feature.properties;
                const speedRatio = props.current_speed / props.free_flow_speed;
                let color = "#008000";
                if (speedRatio < 0.7) color = "#FFA500";
                if (speedRatio < 0.4) color = "#FF0000";

                if (feature.geometry.type === "LineString") {
                  const latlngs = coordinates.map(([lon, lat]) => [lat, lon]);
                  return <Polyline key={`traffic-line-${i}`} positions={latlngs} pathOptions={{ color, weight: 5, opacity: 0.7 }}/>
                }

                return (
                    <CircleMarker
                        key={`traffic-point-${i}`}
                        center={center}
                        radius={8}
                        pathOptions={{ color, fillColor: color, fillOpacity: 0.8 }}
                    />
                );
              })}
            </LayerGroup>
          </Overlay>

        </LayersControl>
      </MapContainer>
  );
}