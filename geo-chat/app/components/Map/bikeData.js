export const bikesData = {
  type: "FeatureCollection",
  features: [
    {
      type: "Feature",
      geometry: {
        type: "Point",
        coordinates: [21.0122, 52.2297]
      },
      properties: {
        name: "Rondo Dmowskiego",
        city: "Warsaw",
        country: "Poland",
        bikes_available: 10,
        docks_available: 5,
        rental_key: 37201,
        spot_id: 123456,
        system_brand: "Veturilo",
        available_bike_types: [
          { type_name: "Typ roweru: ID 71", available_count: 8 },
          { type_name: "Typ roweru: ID 229", available_count: 2 }
        ],
        timestamp: "2025-11-14T18:30:00.000000+00:00"
      }
    }
  ]
};
