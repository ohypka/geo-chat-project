export const trafficData = {
  type: "FeatureCollection",
  features: [
    {
      type: "Feature",
      geometry: {
        type: "LineString",
        coordinates: [
          [23.1688, 53.1325],
          [23.1700, 53.1330],
          [23.1720, 53.1340],
          [23.1740, 53.1350]
        ]
      },
      properties: {
        category: "traffic",
        location_name: "Bialystok Main Street",
        confidence: 1,
        current_speed: 32,
        free_flow_speed: 32,
        source: "tomtom",
        timestamp: "2025-11-11T20:18:11.687366+00:00"
      }
    },
    {
      type: "Feature",
      geometry: {
        type: "LineString",
        coordinates: [
          [23.1750, 53.1360],
          [23.1770, 53.1370],
          [23.1800, 53.1380]
        ]
      },
      properties: {
        category: "traffic",
        location_name: "Bialystok Secondary Road",
        confidence: 0.9,
        current_speed: 18,
        free_flow_speed: 40,
        source: "tomtom",
        timestamp: "2025-11-11T20:20:11.687366+00:00"
      }
    }
  ]
};
