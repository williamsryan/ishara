import React, { useState } from "react";
import { Paper, Typography } from "@mui/material";
import Plot from "react-plotly.js";
import GridLayout from "react-grid-layout";
import "react-grid-layout/css/styles.css";
import "react-resizable/css/styles.css";

const ChartingPage = () => {
    // Initial layout configuration
    const initialLayout = [
        { i: "chart1", x: 0, y: 0, w: 6, h: 8 }, // Chart 1: half width
        { i: "chart2", x: 6, y: 0, w: 6, h: 8 }, // Chart 2: half width
        { i: "chart3", x: 0, y: 8, w: 12, h: 8 }, // Chart 3: full width
    ];

    // State to store and persist the layout
    const [layout, setLayout] = useState(initialLayout);

    // Handle layout change (updates on drag/resize)
    const handleLayoutChange = (newLayout) => {
        setLayout(newLayout);
    };

    return (
        <GridLayout
            className="layout"
            layout={layout}
            cols={12}
            rowHeight={30}
            width={1200}
            isResizable
            isDraggable
            draggableHandle=".drag-handle"
            onLayoutChange={handleLayoutChange} // Save layout changes
        >
            {/* Chart 1 Tile */}
            <div key="chart1">
                <Paper style={{ padding: "16px", height: "100%" }}>
                    <Typography variant="h6" className="drag-handle" style={{ marginBottom: "16px", cursor: "move" }}>
                        Stock Price Chart
                    </Typography>
                    <Plot
                        data={[
                            {
                                x: ["2025-01-01", "2025-01-02", "2025-01-03"],
                                y: [222.5, 223.0, 224.0],
                                type: "scatter",
                                mode: "lines+markers",
                                line: { color: "#3b82f6", width: 2 },
                            },
                        ]}
                        layout={{
                            title: "Stock Price",
                            xaxis: { title: "Date" },
                            yaxis: { title: "Price (USD)" },
                            margin: { t: 30, r: 30, l: 50, b: 50 },
                            responsive: true,
                        }}
                        style={{ width: "100%", height: "100%" }}
                        useResizeHandler={true}
                    />
                </Paper>
            </div>

            {/* Chart 2 Tile */}
            <div key="chart2">
                <Paper style={{ padding: "16px", height: "100%" }}>
                    <Typography variant="h6" className="drag-handle" style={{ marginBottom: "16px", cursor: "move" }}>
                        Volume Chart
                    </Typography>
                    <Plot
                        data={[
                            {
                                x: ["2025-01-01", "2025-01-02", "2025-01-03"],
                                y: [12000, 15000, 18000],
                                type: "bar",
                                marker: { color: "#FF5722" },
                            },
                        ]}
                        layout={{
                            title: "Volume",
                            xaxis: { title: "Date" },
                            yaxis: { title: "Volume" },
                            margin: { t: 30, r: 30, l: 50, b: 50 },
                            responsive: true,
                        }}
                        style={{ width: "100%", height: "100%" }}
                        useResizeHandler={true}
                    />
                </Paper>
            </div>

            {/* Chart 3 Tile */}
            <div key="chart3">
                <Paper style={{ padding: "16px", height: "100%" }}>
                    <Typography variant="h6" className="drag-handle" style={{ marginBottom: "16px", cursor: "move" }}>
                        Cumulative Returns
                    </Typography>
                    <Plot
                        data={[
                            {
                                x: ["2025-01-01", "2025-01-02", "2025-01-03"],
                                y: [1.02, 1.04, 1.06],
                                type: "scatter",
                                mode: "lines+markers",
                                line: { color: "#4CAF50", width: 2 },
                            },
                        ]}
                        layout={{
                            title: "Cumulative Returns",
                            xaxis: { title: "Date" },
                            yaxis: { title: "Return Multiplier" },
                            margin: { t: 30, r: 30, l: 50, b: 50 },
                            responsive: true,
                        }}
                        style={{ width: "100%", height: "100%" }}
                        useResizeHandler={true}
                    />
                </Paper>
            </div>
        </GridLayout>
    );
};

export default ChartingPage;
