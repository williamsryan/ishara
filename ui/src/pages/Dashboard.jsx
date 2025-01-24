import React from "react";
import { Grid2, Paper, Typography, Table, TableBody, TableCell, TableContainer, TableHead, TableRow } from "@mui/material";
import Plot from "react-plotly.js";

const Dashboard = () => {
    const stockData = [
        { symbol: "AAPL", price: 145.2, change: "+0.38%" },
        { symbol: "GOOG", price: 2843.5, change: "-0.12%" },
        { symbol: "TSLA", price: 714.6, change: "+1.08%" },
    ];

    return (
        <Grid2 container spacing={2} style={{ padding: "16px" }}>
            {/* Watchlist */}
            <Grid2 item xs={4}>
                <Paper style={{ padding: "16px", height: "400px" }}>
                    <Typography variant="h6" style={{ marginBottom: "16px" }}>Watchlist</Typography>
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
            </Grid2>

            {/* Price Chart */}
            <Grid2 item xs={8}>
                <Paper style={{ padding: "16px", height: "400px", display: "flex", justifyContent: "center", alignItems: "center" }}>
                    <Typography variant="h6" style={{ marginBottom: "16px" }}>
                        Price Chart
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
                            title: "AAPL Stock Price",
                            xaxis: { title: "Date" },
                            yaxis: { title: "Price (USD)" },
                            margin: { t: 30, r: 30, l: 30, b: 30 },
                            responsive: true,
                        }}
                        style={{ width: "100%", height: "100%" }}
                    />
                </Paper>
            </Grid2>
        </Grid2>
    );
};

export default Dashboard;
