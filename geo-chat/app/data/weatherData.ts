export const weatherData = {
  type: "FeatureCollection",
  features: [
    // Humid + cold → Rainy / Cloudy
    {
      type: "Feature",
      geometry: {
        type: "Point",
        coordinates: [21.0122, 52.2297], // center
      },
      properties: {
        category: "environment",
        location: { lat: 52.2297, lon: 21.0122, name: "Warsaw" },
        metrics: {
          temperature: 8,
          humidity: 80,
          pressure: 1020,
          pm25: 12,
          pm10: 15,
          aqi: 2,
        },
        type: "weather",
      },
    },
    // Low temp + low humidity → Cloudy & Dry
    {
      type: "Feature",
      geometry: {
        type: "Point",
        coordinates: [21.0500, 52.2500], // northeast
      },
      properties: {
        category: "environment",
        location: { lat: 52.2500, lon: 21.0500, name: "Warsaw" },
        metrics: {
          temperature: 9,
          humidity: 40,
          pressure: 1023,
          pm25: 10,
          pm10: 14,
          aqi: 1,
        },
        type: "weather",
      },
    },
    // High temp + low humidity → Sunny
    {
      type: "Feature",
      geometry: {
        type: "Point",
        coordinates: [20.9800, 52.2100], // southwest
      },
      properties: {
        category: "environment",
        location: { lat: 52.2100, lon: 20.9800, name: "Warsaw" },
        metrics: {
          temperature: 28,
          humidity: 30,
          pressure: 1018,
          pm25: 20,
          pm10: 25,
          aqi: 3,
        },
        type: "weather",
      },
    },
   
  ],
};
