import React from "react";
import { Paper, Typography, Table, TableBody, TableCell, TableContainer, TableHead, TableRow } from "@mui/material";
import Plot from "react-plotly.js";
import GridLayout from "react-grid-layout";
import "react-grid-layout/css/styles.css";
import "react-resizable/css/styles.css";

const Dashboard = () => {
    const stockData = [
        { symbol: "AAPL", price: 145.2, change: "+0.38%" },
        { symbol: "GOOG", price: 2843.5, change: "-0.12%" },
        { symbol: "TSLA", price: 714.6, change: "+1.08%" },
    ];

    // Layout definition for ReactGridLayout
    const layout = [
        { i: "watchlist", x: 0, y: 0, w: 4, h: 8 }, // Watchlist: 4 columns wide, 8 rows tall
        { i: "chart", x: 4, y: 0, w: 8, h: 8 },     // Chart: 8 columns wide, 8 rows tall
    ];

    return (
        <GridLayout
            className="layout"
            layout={layout}
            cols={12} // Total columns
            rowHeight={30} // Height of one grid row
            width={1200} // Width of the grid in pixels
            isResizable // Enable resizing
            isDraggable // Enable dragging
            draggableHandle=".drag-handle" // Only allow dragging by the handle
        >
            {/* Watchlist Tile */}
            <div key="watchlist">
                <Paper style={{ padding: "16px", height: "100%" }}>
                    <Typography variant="h6" className="drag-handle" style={{ marginBottom: "16px", cursor: "move" }}>
                        Watchlist
                    </Typography>
                    <TableContainer>
                        <Table>
                            <TableHead>
                                <TableRow>
                                    <TableCell><strong>Symbol</strong></TableCell>
                                    <TableCell align="right"><strong>Price</strong></TableCell>
                                    <TableCell align="right"><strong>Change</strong></TableCell>
                                </TableRow>
                            </TableHead>
                            <TableBody>
                                {stockData.map((stock) => (
                                    <TableRow key={stock.symbol}>
                                        <TableCell>{stock.symbol}</TableCell>
                                        <TableCell align="right">${stock.price.toFixed(2)}</TableCell>
                                        <TableCell align="right" style={{ color: stock.change.startsWith("-") ? "red" : "green" }}>
                                            {stock.change}
                                        </TableCell>
                                    </TableRow>
                                ))}
                            </TableBody>
                        </Table>
                    </TableContainer>
                </Paper>
            </div>

            {/* Price Chart Tile */}
            <div key="chart">
                <Paper style={{ padding: "16px", height: "100%" }}>
                    <Typography variant="h6" className="drag-handle" style={{ marginBottom: "16px", cursor: "move" }}>
                        Price Chart
                    </Typography>
                    <div style={{ height: "calc(100% - 50px)" }}>
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
                                title: "",
                                xaxis: { title: "Date" },
                                yaxis: { title: "Price (USD)" },
                                margin: { t: 30, r: 30, l: 50, b: 50 },
                                responsive: true,
                            }}
                            style={{ width: "100%", height: "100%" }}
                            useResizeHandler={true}
                        />
                    </div>
                </Paper>
            </div>
        </GridLayout>
    );
};

export default Dashboard;
