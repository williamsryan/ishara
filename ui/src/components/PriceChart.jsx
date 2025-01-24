import React from "react";
import Plot from "react-plotly.js";

const PriceChart = () => {
    const data = [
        {
            x: ["2025-01-01", "2025-01-02", "2025-01-03"],
            y: [222.5, 223.0, 224.0],
            type: "scatter",
            mode: "lines+markers",
            line: { color: "#3b82f6", width: 2 },
        },
    ];

    const layout = {
        title: "AAPL Price Chart",
        xaxis: { title: "Date", showgrid: true },
        yaxis: { title: "Price (USD)", showgrid: true },
        margin: { t: 50, l: 50, r: 20, b: 50 },
    };

    return (
        <div style={{ width: "100%", height: "100%" }}>
            <Plot data={data} layout={layout} useResizeHandler style={{ width: "100%", height: "100%" }} />
        </div>
    );
};

export default PriceChart;
