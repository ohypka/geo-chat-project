import { Marker, Popup } from "react-leaflet";
import L from "leaflet";

// Base icons
const iconMap = {
    doctor: "/doctor.webp",
    bike: "/bike.png",
    weather_sunny: "/sunny.png",
    weather_cloudy: "/cloudy.png",
    weather_rain: "/rain.png",
    weather_humid_hot: "/humid_hot.png", // placeholder for high temp + high humidity
    default: "/doctor.webp",
};

// Create Leaflet icon from URL
function createIcon(url) {
    return new L.Icon({
        iconUrl: url,
        iconSize: [32, 32],
        iconAnchor: [16, 32],
        popupAnchor: [0, -32],
    });
}

// Choose weather icon based on temperature & humidity
function chooseWeatherIcon(metrics) {
    if (!metrics) return iconMap.weather_sunny; // fallback

    const temp = metrics.temperature ?? 0;
    const humidity = metrics.humidity ?? 0;

    // Simple thresholds (can be tweaked)
    const lowTemp = temp < 15;
    const highTemp = temp >= 15;
    const lowHumidity = humidity < 60;
    const highHumidity = humidity >= 60;

    if (lowTemp && lowHumidity) return iconMap.weather_cloudy;
    if (lowTemp && highHumidity) return iconMap.weather_rain;
    if (highTemp && lowHumidity) return iconMap.weather_sunny;
    if (highTemp && highHumidity) return iconMap.weather_humid_hot;

    return iconMap.weather_sunny;
}

// Render values nicely
function renderValue(value, key) {
    if (Array.isArray(value)) {
        return value
            .map(v => (typeof v === "object" ? JSON.stringify(v, null, 2) : v))
            .join(", ");
    } else if (typeof value === "object" && value !== null) {
        if (key === "location") return `Name: ${value.name}, Lat: ${value.lat}, Lon: ${value.lon}`;
        if (key === "metrics") return Object.entries(value)
            .map(([metric, val]) => `${metric.toUpperCase()}: ${val}`)
            .join(", ");
        return JSON.stringify(value, null, 2);
    }
    return value?.toString();
}

export default function MapMarker({ marker,showPopup = true }) {
    // Safety checks
    if (!marker || !marker.geometry || !marker.geometry.coordinates || marker.geometry.coordinates.length < 2 || !marker.properties) return null;

    const { coordinates } = marker.geometry;
    const properties = marker.properties;

    // Decide icon
    let icon;
    if (properties.type === "weather") {
        icon = createIcon(chooseWeatherIcon(properties.metrics));
    } else {
        const type = properties.type || "doctor";
        icon = createIcon(iconMap[type] || iconMap.default);
    }

    return (
        <Marker position={[coordinates[1], coordinates[0]]} icon={icon}>
            {showPopup &&
            <Popup>
                <div style={{ textAlign: "center" }}>
                    <h3>{properties.place || properties.title || properties.name || properties.location?.name || "No Title"}</h3>

                    {/* Display all fields dynamically except 'type' */}
                    {Object.entries(properties)
                        .filter(([key]) => key !== "type")
                        .map(([key, value]) => (
                            <p key={key}>
                                <span style={{ fontWeight: "bold" }}>{key.toUpperCase()}:</span>{" "}
                                {renderValue(value, key)}
                            </p>
                        ))}

                    <button
                        onClick={() =>
                            alert(`Action for ${properties.place || properties.title || properties.name || properties.location?.name || "this marker"}`)
                        }
                        style={{
                            padding: "5px 10px",
                            background: "#1E90FF",
                            color: "white",
                            border: "none",
                            borderRadius: 4,
                            marginTop: 5,
                        }}
                    >
                        Action
                    </button>
                </div>
            </Popup>}
        </Marker>
    );
}
