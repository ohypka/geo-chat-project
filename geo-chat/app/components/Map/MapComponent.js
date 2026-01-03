"use client";

import { useEffect } from "react";
import L from "leaflet";
import "leaflet/dist/leaflet.css";

//Location data
import { weatherData } from "./weatherData";
import { doctorsData } from "./doctorsData";
import { trafficData } from "./trafficData";
import { bikesData } from "./bikeData";



let mapInstance;

export default function MapComponent() {
    useEffect(() => {
        if (mapInstance) {
            mapInstance.remove();
            mapInstance = null;
        }

        mapInstance = L.map("map").setView([52.2297, 21.0122], 13);

        L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
            maxZoom: 19,
        }).addTo(mapInstance);

        //Weather Layer
        const weatherLayer = L.layerGroup();
        weatherData.features.forEach((feature) => {
            const { coordinates } = feature.geometry;
            const { metrics, location } = feature.properties;

            const temp = metrics?.temperature ?? 0;
            let color = "#1E90FF";
            if (temp >= 25) color = "#FF4500";
            else if (temp >= 15) color = "#FFA500";
            else if (temp >= 5) color = "#FFFF00";

            const circle = L.circleMarker([coordinates[1], coordinates[0]], {
                radius: 12,
                fillColor: color,
                color: "#000",
                weight: 1,
                opacity: 1,
                fillOpacity: 0.8,
            }).bindPopup(`
        <b>${location.name}</b><br>
        Temp: ${temp} °C<br>
        Humidity: ${metrics?.humidity ?? "-"}%<br>
        Pressure: ${metrics?.pressure ?? "-"} hPa<br>
        PM2.5: ${metrics?.pm25 ?? "-"}<br>
        PM10: ${metrics?.pm10 ?? "-"}<br>
        AQI: ${metrics?.aqi ?? "-"}
      `);

            weatherLayer.addLayer(circle);
        });
        weatherLayer.addTo(mapInstance);

        //Doctors Layer
        const doctorsLayer = L.layerGroup();
        doctorsData.features.forEach((feature) => {
            const { coordinates } = feature.geometry;
            const props = feature.properties;

            const marker = L.circleMarker([coordinates[1], coordinates[0]], {
                radius: 10,
                fillColor: "#FF69B4",
                color: "#000",
                weight: 1,
                opacity: 1,
                fillOpacity: 0.8,
            }).bindPopup(`
        <b>${props.place}</b><br>
        Provider: ${props.provider}<br>
        Address: ${props.address}<br>
        Phone: ${props.phone}<br>
        Service: ${props.service}<br>
        Waiting days: ${props.waiting_days}<br>
        Queue date: ${props.queue_date}
      `);

            doctorsLayer.addLayer(marker);
        });
        doctorsLayer.addTo(mapInstance);

        //Traffic Layer
        const trafficLayer = L.layerGroup();
        trafficData.features.forEach((feature) => {
            const { coordinates } = feature.geometry;
            const props = feature.properties;

            // TODO: create a line based on speed
            const speedRatio = props.current_speed / props.free_flow_speed;
            let color = "#008000";
            if (speedRatio < 0.7) color = "#FFA500";
            if (speedRatio < 0.4) color = "#FF0000";

            const circle = L.circleMarker([coordinates[1], coordinates[0]], {
                radius: 12,
                fillColor: color,
                color: "#000",
                weight: 1,
                opacity: 1,
                fillOpacity: 0.8,
            }).bindPopup(`
        <b>${props.location_name}</b><br>
        Current speed: ${props.current_speed} km/h<br>
        Free flow speed: ${props.free_flow_speed} km/h<br>
        Confidence: ${props.confidence}<br>
        Source: ${props.source}
      `);

            trafficLayer.addLayer(circle);
        });
        trafficLayer.addTo(mapInstance);


        //Bikes Layer
        const bikesLayer = L.layerGroup();
        bikesData.features.forEach((feature) => {
            const { coordinates } = feature.geometry;
            const props = feature.properties;

            let color = "#640000ff";
            if (props.bikes_available >= 5 && props.bikes_available < 10) color = "#FFA500";
            if (props.bikes_available >= 10) color = "#00ff00ff";

            const marker = L.circleMarker([coordinates[1], coordinates[0]], {
                radius: 10,
                fillColor: color,
                color: "#000",
                weight: 1,
                opacity: 1,
                fillOpacity: 0.8
            }).bindPopup(`
    <b>${props.name}</b><br>
    City: ${props.city}<br>
    Bikes available: ${props.bikes_available}<br>
    Docks available: ${props.docks_available}<br>
    System: ${props.system_brand}<br>
    Rental key: ${props.rental_key}<br>
    Spot ID: ${props.spot_id}
  `);

            bikesLayer.addLayer(marker);
        });

        bikesLayer.addTo(mapInstance);

        //Filtering by layers
        L.control.layers(
            null,
            {
                Weather: weatherLayer,
                Doctors: doctorsLayer,
                Traffic: trafficLayer,
                Bikes: bikesLayer
            },
            { collapsed: false }
        ).addTo(mapInstance);

        return () => {
            if (mapInstance) {
                mapInstance.remove();
                mapInstance = null;
            }
        };
    }, []);

    return <div id="map" style={{ width: "100%", height: "100vh" }} />;
}
