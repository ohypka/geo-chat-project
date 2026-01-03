export const weatherData = {
  type: "FeatureCollection",
  features: [
    {
      type: "Feature",
      geometry: {
        type: "Point",
        coordinates: [21.0122, 52.2297]
      },
      properties: {
        category: "environment",
        location: {
          lat: 52.2297,
          lon: 21.0122,
          name: "Warsaw"
        },
        metrics: {
          temperature: 10.18,
          humidity: 77,
          pressure: 1021,
          pm25: 12.56,
          pm10: 16.61,
          aqi: 2
        }
      }
    }
  ]
};
