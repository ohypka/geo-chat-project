"use client";

import { useEffect, useState } from "react";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import {
  fetchEnvironmentData,
  fetchDoctorsCoordinates,
  fetchTrafficData,
  fetchBikesData,
  type EnvironmentData,
  type DoctorsResponse,
  type TrafficData,
  type BikeData,
} from "@/lib/api";

let mapInstance: L.Map | null = null;

// Default location: Warsaw
const DEFAULT_LAT = 52.2297;
const DEFAULT_LON = 21.0122;

export default function MapComponent() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [weatherData, setWeatherData] = useState<EnvironmentData | null>(null);
  const [doctorsData, setDoctorsData] = useState<DoctorsResponse | null>(null);
  const [trafficData, setTrafficData] = useState<TrafficData | null>(null);
  const [bikesData, setBikesData] = useState<BikeData[] | null>(null);

  useEffect(() => {
    // Fetch data from APIs
    const loadData = async () => {
      setLoading(true);
      setError(null);

      try {
        // Fetch all data in parallel
        const [envData, doctorsResp, trafficResp, bikesResp] = await Promise.allSettled([
          fetchEnvironmentData(DEFAULT_LAT, DEFAULT_LON, "Warsaw"),
          fetchDoctorsCoordinates(DEFAULT_LAT, DEFAULT_LON, "KARDIOLOG", false),
          fetchTrafficData(DEFAULT_LAT, DEFAULT_LON, "Warsaw"),
          fetchBikesData(),
        ]);

        if (envData.status === "fulfilled" && envData.value) {
          setWeatherData(envData.value);
        } else {
          if (envData.status === "rejected") {
            console.warn("Weather data not available:", envData.reason);
          }
        }

        if (doctorsResp.status === "fulfilled") {
          setDoctorsData(doctorsResp.value);
        } else {
          console.error("Failed to fetch doctors data:", doctorsResp.reason);
        }

        if (trafficResp.status === "fulfilled" && trafficResp.value) {
          setTrafficData(trafficResp.value);
        } else {
          if (trafficResp.status === "rejected") {
            console.warn("Traffic data not available:", trafficResp.reason);
          }
        }

        if (bikesResp.status === "fulfilled" && bikesResp.value) {
          setBikesData(bikesResp.value);
        } else {
          if (bikesResp.status === "rejected") {
            console.warn("Bikes data not available:", bikesResp.reason);
          }
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load data");
        console.error("Error loading data:", err);
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, []);

  useEffect(() => {
    if (loading) return;

    // Initialize map
    if (mapInstance) {
      mapInstance.remove();
      mapInstance = null;
    }

    mapInstance = L.map("map").setView([DEFAULT_LAT, DEFAULT_LON], 13);

    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      maxZoom: 19,
    }).addTo(mapInstance);

    const layers: Record<string, L.LayerGroup> = {};

    // Weather Layer
    if (weatherData) {
      const weatherLayer = L.layerGroup();
      const { lat, lon } = weatherData.location;
      const { metrics } = weatherData;

      const temp = metrics?.temperature ?? 0;
      let color = "#1E90FF";
      if (temp >= 25) color = "#FF4500";
      else if (temp >= 15) color = "#FFA500";
      else if (temp >= 5) color = "#FFFF00";

      const circle = L.circleMarker([lat, lon], {
        radius: 12,
        fillColor: color,
        color: "#000",
        weight: 1,
        opacity: 1,
        fillOpacity: 0.8,
      }).bindPopup(`
        <b>${weatherData.location.name || "Location"}</b><br>
        Temp: ${temp} °C<br>
        Humidity: ${metrics?.humidity ?? "-"}%<br>
        Pressure: ${metrics?.pressure ?? "-"} hPa<br>
        PM2.5: ${metrics?.pm25 ?? "-"}<br>
        PM10: ${metrics?.pm10 ?? "-"}<br>
        AQI: ${metrics?.aqi ?? "-"}
      `);

      weatherLayer.addLayer(circle);
      weatherLayer.addTo(mapInstance);
      layers["Weather"] = weatherLayer;
    }

    if (doctorsData && doctorsData.results.length > 0) {
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

      const doctorsLayer = L.layerGroup();
      
      const coordinateMap = new Map<string, number>();
      
      validResults.forEach((doctor, index) => {
        if (doctor.lat && doctor.lon) {
          const daysUntil = getDaysUntilAppointment(doctor.queue_date);
          let waitingText = "";
          if (daysUntil === 0) {
            waitingText = "DZISIAJ";
          } else if (daysUntil === 1) {
            waitingText = "1 dzień";
          } else {
            waitingText = `${daysUntil} dni`;
          }

          const coordKey = `${doctor.lat.toFixed(4)},${doctor.lon.toFixed(4)}`;
          let offsetCount = coordinateMap.get(coordKey) || 0;
          coordinateMap.set(coordKey, offsetCount + 1);
          
          const offsetLat = doctor.lat + (offsetCount * 0.002);
          const offsetLon = doctor.lon + (offsetCount * 0.002);

          const marker = L.circleMarker([offsetLat, offsetLon], {
            radius: 10,
            fillColor: "#FF69B4",
            color: "#000",
            weight: 1,
            opacity: 1,
            fillOpacity: 0.8,
          }).bindPopup(`
            <b>${doctor.place || doctor.provider}</b><br>
            ${doctor.provider && doctor.place !== doctor.provider ? `Provider: ${doctor.provider}<br>` : ""}
            Adres: ${doctor.address || "Brak"}<br>
            Telefon: ${doctor.phone || "Brak"}<br>
            Usługa: ${doctor.service || "Brak"}<br>
            Czas oczekiwania: ${waitingText}<br>
            Data kolejki: ${doctor.queue_date || "Brak"}
          `);

          doctorsLayer.addLayer(marker);
        }
      });
      
      if (doctorsLayer.getLayers().length > 0) {
        doctorsLayer.addTo(mapInstance);
        layers["Doctors"] = doctorsLayer;
      }
    }

    // Traffic Layer
    if (trafficData) {
      const trafficLayer = L.layerGroup();
      const { lat, lon } = trafficData.location;
      const { metrics } = trafficData;

      const currentSpeed = metrics?.current_speed ?? 0;
      const freeFlowSpeed = metrics?.free_flow_speed ?? 1;
      const speedRatio = currentSpeed / freeFlowSpeed;
      let color = "#008000";
      if (speedRatio < 0.7) color = "#FFA500";
      if (speedRatio < 0.4) color = "#FF0000";

      const circle = L.circleMarker([lat, lon], {
        radius: 12,
        fillColor: color,
        color: "#000",
        weight: 1,
        opacity: 1,
        fillOpacity: 0.8,
      }).bindPopup(`
        <b>${metrics?.location_name || "Location"}</b><br>
        Current speed: ${currentSpeed} km/h<br>
        Free flow speed: ${freeFlowSpeed} km/h<br>
        Confidence: ${metrics?.confidence ?? "-"}<br>
        Source: ${trafficData.source}
      `);

      trafficLayer.addLayer(circle);
      trafficLayer.addTo(mapInstance);
      layers["Traffic"] = trafficLayer;
    }

    // Bikes Layer
    if (bikesData && bikesData.length > 0) {
      const bikesLayer = L.layerGroup();
      bikesData.forEach((bike) => {
        let color = "#640000ff";
        if (bike.bikes_available >= 5 && bike.bikes_available < 10) color = "#FFA500";
        if (bike.bikes_available >= 10) color = "#00ff00ff";

        const marker = L.circleMarker([bike.lat, bike.lon], {
          radius: 10,
          fillColor: color,
          color: "#000",
          weight: 1,
          opacity: 1,
          fillOpacity: 0.8,
        }).bindPopup(`
          <b>${bike.name}</b><br>
          City: ${bike.city}<br>
          Bikes available: ${bike.bikes_available}<br>
          Docks available: ${bike.docks_available}<br>
          System: ${bike.system_brand}<br>
          ${bike.rental_key ? `Rental key: ${bike.rental_key}<br>` : ""}
          ${bike.spot_id ? `Spot ID: ${bike.spot_id}` : ""}
        `);

        bikesLayer.addLayer(marker);
      });
      bikesLayer.addTo(mapInstance);
      layers["Bikes"] = bikesLayer;
    }

    // Add layer control
    if (Object.keys(layers).length > 0) {
      L.control.layers(null, layers, { collapsed: false }).addTo(mapInstance);
    }

    return () => {
      if (mapInstance) {
        mapInstance.remove();
        mapInstance = null;
      }
    };
  }, [loading, weatherData, doctorsData, trafficData, bikesData]);

  if (loading) {
    return (
      <div
        id="map"
        style={{
          width: "100%",
          height: "100vh",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          backgroundColor: "#1a1a1a",
          color: "#fff",
        }}
      >
        <div>Ładowanie danych z API...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div
        id="map"
        style={{
          width: "100%",
          height: "100vh",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          backgroundColor: "#1a1a1a",
          color: "#ff4444",
          flexDirection: "column",
          gap: "1rem",
        }}
      >
        <div>Błąd: {error}</div>
        <div style={{ fontSize: "0.875rem", color: "#888" }}>
          Upewnij się, że serwery backendowe są uruchomione.
        </div>
      </div>
    );
  }

  return <div id="map" style={{ width: "100%", height: "100vh" }} />;
}

