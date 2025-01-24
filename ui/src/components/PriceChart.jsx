import React from "react";
import Plot from "react-plotly.js";

const PriceChart = () => {
    const data = [
        {
            x: ["2025-01-01", "2025-01-02", "2025-01-03"],
            y: [222.5, 223.0, 224.0],
            type: "scatter",
            mode: "lines",
            line: { color: "#3b82f6" },
        },
    ];

    return (
        <div style={{ flex: 1, padding: "16px" }}>
            <h3>AAPL (Apple Inc.)</h3>
            <Plot
                data={data}
                layout={{
                    title: "Price Chart",
                    xaxis: { title: "Date" },
                    yaxis: { title: "Price" },
                    responsive: true,
                }}
                style={{ width: "100%", height: "400px" }}
            />
        </div>
    );
};

export default PriceChart;
