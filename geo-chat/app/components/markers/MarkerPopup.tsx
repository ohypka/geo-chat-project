import React from "react";

interface DoctorProperties {
    type: "doctor";
    provider: string;
    address: string;
    locality: string;
    phone: string;
    waiting_days: number;
    service: string;
}

interface BikeProperties {
    type: "bike";
    bikes: number;
    place?: string;
    title?: string;
    name?: string;
    location?: { name: string };
}

interface WeatherProperties {
    type: "weather";
    temperature: number;
    humidity: number;
    pressure: number;
    aqi?: number;
    rain_1h?: number;
    snow_1h?: number;
}

type MapProperties = DoctorProperties | BikeProperties | WeatherProperties;

interface MarkerPopupProps {
    properties: MapProperties;
}

export default function MarkerPopup({ properties }: MarkerPopupProps) {

    function renderPopupContent() {
        console.log(properties)
        switch (properties.type) {

            case "doctor":
                return (
                    <>
                        <p><strong>{properties.provider}</strong></p>
                        <p><strong>Adres:</strong> {properties.address}, {properties.locality}</p>
                        <p><strong>Telefon:</strong> {properties.phone}</p>
                        <p><strong>Czas oczekiwania (dni):</strong> {properties.waiting_days}</p>
                        <p>{properties.service}</p>
                    </>
                );
            case "bike":
                return (
                    <>
                        <p><strong>Stacja:</strong> {properties.place || properties.title || properties.name || properties.location?.name}</p>
                        <p><strong>Dostępne rowery:</strong> {properties.bikes}</p>
                    </>
                );
            case "weather":
                return (
                    <>
                        <p><strong>Temperatura:</strong> {properties.temperature ?? "N/A"}°C</p>
                        <p><strong>Wilgotność:</strong> {properties.humidity ?? "N/A"}%</p>
                        <p><strong>Ciśnienie:</strong> {properties.pressure?? "N/A"} hPa</p>
                        {/*<p><strong>Jakość powietrza (AQI):</strong> {properties.aqi}</p>
                        <p><strong>Opady deszczu:</strong> {properties.rain_1h} mm</p>
                        <p><strong>Opady śniegu:</strong> {properties.snow_1h} mm</p>
                        <p><strong>PM2.5:</strong> {properties.pm25} µg/m³</p>
                        <p><strong>PM10:</strong> {properties.pm10} µg/m³</p>*/}
                    </>
                );
            default:
                return Object.entries(properties)
                    .filter(([key]) => key !== "type")
                    .map(([key, value]) => (
                        <p key={key}><strong>{key}:</strong> {JSON.stringify(value)}</p>
                    ));
        }
    }

    return (
        <div style={{ textAlign: "left", fontSize: "14px"}}>
            {renderPopupContent()}
        </div>
    );
}
