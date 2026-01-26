export const bikesData = {
  type: "bike",
  features: Array.from({ length: 50 }, (_, i) => {
    // Random small offsets from central Warsaw
    const lat = 52.2297 + (Math.random() - 0.5) * 0.1;  // ±0.05
    const lon = 21.0122 + (Math.random() - 0.5) * 0.1;  // ±0.05

    const bikes_available = Math.floor(Math.random() * 15); // 0–14 bikes
    const docks_available = Math.floor(Math.random() * 10); // 0–9 docks

    return {
      type: "Feature",
      geometry: {
        type: "Point",
        coordinates: [lon, lat],
      },
      properties: {
        name: `Bike Station ${i + 1}`,
        city: "Warsaw",
        country: "Poland",
        bikes_available,
        docks_available,
        rental_key: 37000 + i,
        spot_id: 100000 + i,
        system_brand: "Veturilo",
        available_bike_types: [
          { type_name: "Typ roweru: ID 71", available_count: Math.floor(bikes_available / 2) },
          { type_name: "Typ roweru: ID 229", available_count: Math.ceil(bikes_available / 2) }
        ],
        timestamp: new Date().toISOString(),
        type: "bike",
      },
    };
  }),
};
