"use client";

import { useState, useEffect } from "react";
import { MapContainer, TileLayer, CircleMarker, Polyline, Tooltip, LayersControl, LayerGroup } from "react-leaflet";
import MarkerClusterGroup from 'react-leaflet-markercluster';
import MapMarker from "../markers/DoctorMarker.js";
import { doctorsData } from "../../data/doctorsData.js";
import { weatherData } from "../../data/weatherData.js";
import { trafficData } from "../../data/trafficData.js";
import { bikesData } from "../../data/bikeData.js";
import "leaflet/dist/leaflet.css";

const { Overlay } = LayersControl;

export default function MapComponent() {
  const [isClient, setIsClient] = useState(false);

  useEffect(() => setIsClient(true), []);
  if (!isClient) return null;

  return (
    <MapContainer center={[52.2297, 21.0122]} zoom={13} style={{ width: "100%", height: "100vh" }}>
      <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />

      <LayersControl position="topright">

        <Overlay name="Doctors" checked>
          <LayerGroup>
            <MarkerClusterGroup>
              {doctorsData.features.map((doc, i) => (
                <MapMarker key={i} marker={doc} />
              ))}
            </MarkerClusterGroup>
          </LayerGroup>
        </Overlay>

        <Overlay name="Weather" checked>
          <LayerGroup>
            <MarkerClusterGroup>
              {weatherData.features.map((feature, i) => {
                const marker = { ...feature, properties: { ...feature.properties, type: "weather" } };
                return <MapMarker key={i} marker={marker} />;
              })}
            </MarkerClusterGroup>
          </LayerGroup>
        </Overlay>

        <Overlay name="Traffic" checked>
          <LayerGroup>
            {trafficData.features.map((feature, i) => {
              const { coordinates } = feature.geometry;
              const props = feature.properties;
              const speedRatio = props.current_speed / props.free_flow_speed;
              let color = "#008000";
              if (speedRatio < 0.7) color = "#FFA500";
              if (speedRatio < 0.4) color = "#FF0000";

              if (coordinates.length >= 2) {
                const latlngs = coordinates.map(([lon, lat]) => [lat, lon]);
                return <Polyline key={i} positions={latlngs} pathOptions={{ color, weight: 5, opacity: 0.7 }} />;
              } else {
                return (
                  <CircleMarker
                    key={i}
                    center={[coordinates[1], coordinates[0]]}
                    radius={8}
                    pathOptions={{ color, fillColor: color, fillOpacity: 0.8 }}
                  />
                );
              }
            })}
          </LayerGroup>
        </Overlay>

        <Overlay name="Bikes" checked>
          <LayerGroup>
            <MarkerClusterGroup>
              {bikesData.features.map((bike, i) => (
                <MapMarker key={i} marker={bike} />
              ))}
            </MarkerClusterGroup>
          </LayerGroup>
        </Overlay>

      </LayersControl>
    </MapContainer>
  );
}
