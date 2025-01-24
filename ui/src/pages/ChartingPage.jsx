import React, { useState, useEffect } from "react";
import { Paper, Typography } from "@mui/material";
import Plot from "react-plotly.js";
import GridLayout from "react-grid-layout";
import "react-grid-layout/css/styles.css";
import "react-resizable/css/styles.css";
import { fetchChartData } from "../utils/api";

const ChartingPage = () => {
    const [chart1Data, setChart1Data] = useState(null);
    const [chart2Data, setChart2Data] = useState(null);
    const [chart3Data, setChart3Data] = useState(null);

    useEffect(() => {
        // Fetch data for all charts
        const fetchData = async () => {
            try {
                const [data1, data2, data3] = await Promise.all([
                    fetchChartData("AAPL"),
                    fetchChartData("GOOG"),
                    fetchChartData("TSLA"),
                ]);
                setChart1Data(data1);
                setChart2Data(data2);
                setChart3Data(data3);
            } catch (error) {
                console.error("Failed to fetch chart data:", error);
            }
        };
        fetchData();
    }, []);

    const layout = [
        { i: "chart1", x: 0, y: 0, w: 6, h: 8 },
        { i: "chart2", x: 6, y: 0, w: 6, h: 8 },
        { i: "chart3", x: 0, y: 8, w: 12, h: 8 },
    ];

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
        >
            {/* Chart 1 */}
            <div key="chart1">
                <Paper style={{ padding: "16px", height: "100%" }}>
                    <Typography variant="h6" className="drag-handle" style={{ marginBottom: "16px", cursor: "move" }}>
                        AAPL Price Chart
                    </Typography>
                    {chart1Data ? (
                        <Plot
                            data={[
                                {
                                    x: chart1Data.dates,
                                    y: chart1Data.prices,
                                    type: "scatter",
                                    mode: "lines",
                                    line: { color: "#3b82f6", width: 2 },
                                },
                            ]}
                            layout={{
                                xaxis: { title: "Date" },
                                yaxis: { title: "Price (USD)" },
                                margin: { t: 30, r: 30, l: 50, b: 50 },
                                responsive: true,
                            }}
                            style={{ width: "100%", height: "100%" }}
                            useResizeHandler
                        />
                    ) : (
                        <p>Loading...</p>
                    )}
                </Paper>
            </div>

            {/* Chart 2 */}
            <div key="chart2">
                <Paper style={{ padding: "16px", height: "100%" }}>
                    <Typography variant="h6" className="drag-handle" style={{ marginBottom: "16px", cursor: "move" }}>
                        GOOG Volume Chart
                    </Typography>
                    {chart2Data ? (
                        <Plot
                            data={[
                                {
                                    x: chart2Data.dates,
                                    y: chart2Data.volumes,
                                    type: "bar",
                                    marker: { color: "#FF5722" },
                                },
                            ]}
                            layout={{
                                xaxis: { title: "Date" },
                                yaxis: { title: "Volume" },
                                margin: { t: 30, r: 30, l: 50, b: 50 },
                                responsive: true,
                            }}
                            style={{ width: "100%", height: "100%" }}
                            useResizeHandler
                        />
                    ) : (
                        <p>Loading...</p>
                    )}
                </Paper>
            </div>

            {/* Chart 3 */}
            <div key="chart3">
                <Paper style={{ padding: "16px", height: "100%" }}>
                    <Typography variant="h6" className="drag-handle" style={{ marginBottom: "16px", cursor: "move" }}>
                        TSLA Returns Chart
                    </Typography>
                    {chart3Data ? (
                        <Plot
                            data={[
                                {
                                    x: chart3Data.dates,
                                    y: chart3Data.returns,
                                    type: "scatter",
                                    mode: "lines",
                                    line: { color: "#4CAF50", width: 2 },
                                },
                            ]}
                            layout={{
                                xaxis: { title: "Date" },
                                yaxis: { title: "Return Multiplier" },
                                margin: { t: 30, r: 30, l: 50, b: 50 },
                                responsive: true,
                            }}
                            style={{ width: "100%", height: "100%" }}
                            useResizeHandler
                        />
                    ) : (
                        <p>Loading...</p>
                    )}
                </Paper>
            </div>
        </GridLayout>
    );
};

export default ChartingPage;
