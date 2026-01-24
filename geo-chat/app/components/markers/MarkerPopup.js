import React from "react";

export default function MarkerPopup({ properties }) {

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
                        <p><strong>Ciśnienie:</strong> {properties.pressure?? "N/A"}</p>
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
