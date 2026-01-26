import { Marker, Popup,Tooltip } from "react-leaflet";
import L from "leaflet";
import MarkerPopup from "./MarkerPopup";

interface MarkerProps {
    marker: {
        geometry: {
            type: string;
            coordinates: [number, number];
        };
        properties: any;
    };
    showPopup?: boolean;
}

const tooltipStyles = `
  .leaflet-tooltip.custom-tooltip {
    background-color: transparent;
    border: none;
    box-shadow: none;
    padding: 0;
  }
`;
// Base icons
const iconMap = {
    doctor: "/doctor.png",
    bike: "/bike.png",
    weather_sunny: "/sunny.png",
    weather_cloudy: "/cloudy.png",
    weather_rain: "/rain.png",
    weather_snow: "/snow.png",
    weather_humid_hot: "/humid_hot.png", // placeholder for high temp + high humidity
    default: "/doctor.png",
};

// Create Leaflet icon from URL
function createWeatherIcon(url:string,size:number =40) {
    return new L.Icon({
        iconUrl: url,
        iconSize: [size, size],
        iconAnchor: [size / 2, size],
        popupAnchor: [0, -size]
    });
}
function createIcon({
    url,
    color = "#1E90FF",
    size = 40
}: { url: string; color?: string; size?: number }) {
    return L.divIcon({
        className: "",
        html: `
            <div style="
                width:${size}px;
                height:${size}px;
                background:${color};
                border-radius:50%;
                display:flex;
                align-items:center;
                justify-content:center;
                border:1px solid white;
                box-shadow:0 0 6px rgba(0,0,0,0.4);
            ">
                <img src="${url}" alt="weather icon" style="
                    width:${size * 0.7}px;
                    height:${size * 0.7}px;
                "/>
            </div>
        `,
        iconSize: [size, size],
        iconAnchor: [size / 2, size],
        popupAnchor: [0, -size]
    });
}

// Choose weather icon based on temperature & humidity
function chooseWeatherIcon(metrics:any) {
    if (!metrics) return iconMap.weather_sunny; // fallback

    const temp = metrics.temperature ?? 0;
    const humidity = metrics.humidity ?? 0;
    const rain= metrics.rain_1h ?? 0;
    const snow= metrics.snow_1h ?? 0;

    // Simple thresholds (can be tweaked)
    const lowTemp = temp < 15;
    const highTemp = temp >= 15;
    const lowHumidity = humidity < 60;
    const highHumidity = humidity >= 60;

    if (snow > 0) return iconMap.weather_snow;
    if (rain > 0) return iconMap.weather_rain;
    if (lowTemp) return iconMap.weather_cloudy;
    if (highTemp && lowHumidity) return iconMap.weather_sunny;
    if (highTemp && highHumidity) return iconMap.weather_humid_hot;

    return iconMap.weather_sunny;
}

function chooseBikeIcon(bikes_available:number) {
    const url = iconMap.bike;
    const color = bikes_available === 0 ? "#dd2828" : bikes_available>3? "#00c71b":"#e3b707";
    return { url, color };
}

function chooseDoctorIcon(waiting_days:number) {
    const url = iconMap.doctor;
    const color = waiting_days < 5 ?"#00c71b" : waiting_days<14?"#e3b707" :"#dd2828" ;
    return { url, color };
}


// Render values nicely
/*function renderValue(value, key) {
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
}*/

export default function MapMarker({ marker,showPopup = true }:MarkerProps) {
    // Safety checks
    if (!marker || !marker.geometry || !marker.geometry.coordinates || marker.geometry.coordinates.length < 2 || !marker.properties) return null;

    const { coordinates } = marker.geometry;
    const properties = marker.properties;
    const tooltipSize = 40;

    // Decide icon
    let icon;
    if (properties.type === "weather") {
        const weatherUrl = chooseWeatherIcon(properties);
        icon = createWeatherIcon(weatherUrl);
    } else if (properties.type === "bike") {
        const bikeConfig = chooseBikeIcon(properties.bikes);
        icon = createIcon(bikeConfig);
    } else if (properties.type === "doctor") {
        const doctorConfig=chooseDoctorIcon(properties.waiting_days)
        icon = createIcon(doctorConfig);
    } else {
        icon = createIcon({ url: iconMap.default});
    }

    return (<>
        <style>{tooltipStyles}</style>
        <Marker position={[coordinates[1], coordinates[0]]} icon={icon}>
            {properties.type === "weather" && properties.temperature != null && (
                <Tooltip direction="top" offset={[0, -tooltipSize]} className="custom-tooltip" permanent>
                    <div style={{
                        width: `${tooltipSize}px`,
                        height: `${tooltipSize}px`,
                        background:"white",
                        fontSize:"20px",
                        fontWeight:"bold",
                        borderRadius: "50%",
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center",
                        border: "1px solid white",
                        boxShadow: "0 0 6px rgba(0,0,0,0.9)",
                    }}>
                        {`${Math.round(properties.temperature)}°`}
                    </div>
                </Tooltip>
            )}
            {showPopup &&
                <Popup>
                    <MarkerPopup properties={properties}/>
                </Popup>}
        </Marker></>
    );
}
