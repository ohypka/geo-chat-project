export const LEGENDS = {
    bikes: {
        title: "Bike stations",
        items: [
            {
                color: "#00c71b",
                label: "Bikes available (more than 3)"
            },
            {
                color: "#e3b707",
                label: "Limited availability (1–3 bikes)"
            },
            {
                color: "#dd2828",
                label: "No bikes available"
            }
        ],
    },
    traffic: {
        title: "Traffic congestion",
        items: [
            {
                color: "#008000",
                label: "Low congestion (near free-flow traffic)"
            },
            {
                color: "#FFA500",
                label: "Moderate congestion (reduced traffic speed)"
            },
            {
                color: "#FF0000",
                label: "Heavy congestion (severe slowdown)"
            }
        ]
    },
    doctors: {
        title: "Doctors – waiting time",
        items: [
            {
                color: "#00c71b",
                label: "Short waiting time (less than 5 days)"
            },
            {
                color: "#e3b707",
                label: "Moderate waiting time (5–13 days)"
            },
            {
                color: "#dd2828",
                label: "Long waiting time (14 days or more)"
            }
        ]
    }
};