import React, { useEffect, useState } from "react";
import { Paper, Typography, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, CircularProgress, Alert } from "@mui/material";
import Plot from "react-plotly.js";
import GridLayout from "react-grid-layout";
import "react-grid-layout/css/styles.css";
import "react-resizable/css/styles.css";
import { fetchPortfolioData, fetchChartData } from "../utils/api";

const Dashboard = () => {
    const [watchlist, setWatchlist] = useState([]);
    const [selectedSymbol, setSelectedSymbol] = useState("SPY"); // Default stock for chart
    const [chartData, setChartData] = useState(null);
    const [portfolioError, setPortfolioError] = useState(null);
    const [chartError, setChartError] = useState(null);
    const [loadingPortfolio, setLoadingPortfolio] = useState(true);
    const [loadingChart, setLoadingChart] = useState(true);

    useEffect(() => {
        const getPortfolioData = async () => {
            try {
                const data = await fetchPortfolioData();
                setWatchlist(data.stocks || []);
                setLoadingPortfolio(false);
            } catch (err) {
                setPortfolioError("Failed to load portfolio data.");
                setLoadingPortfolio(false);
            }
        };

        getPortfolioData();
    }, []);

    useEffect(() => {
        const getChartData = async () => {
            try {
                const data = await fetchChartData(selectedSymbol);
                setChartData(data);
                setChartError(null);
                setLoadingChart(false);
            } catch (err) {
                setChartError("Failed to load chart data.");
                setLoadingChart(false);
            }
        };

        getChartData();
    }, [selectedSymbol]);

    const layout = [
        { i: "watchlist", x: 0, y: 0, w: 4, h: 8 },
        { i: "chart", x: 4, y: 0, w: 8, h: 8 },
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
            {/* Watchlist Section */}
            <div key="watchlist">
                <Paper style={{ padding: "16px", height: "100%", overflow: "auto" }}>
                    <Typography variant="h6" className="drag-handle" style={{ marginBottom: "16px", cursor: "move" }}>
                        Watchlist
                    </Typography>
                    {loadingPortfolio ? (
                        <CircularProgress />
                    ) : portfolioError ? (
                        <Alert severity="error">{portfolioError}</Alert>
                    ) : (
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
                                    {watchlist.map((stock) => (
                                        <TableRow
                                            key={stock.symbol}
                                            onClick={() => setSelectedSymbol(stock.symbol)}
                                            style={{ cursor: "pointer" }}
                                        >
                                            <TableCell>{stock.symbol}</TableCell>
                                            <TableCell align="right">${stock.current_price?.toFixed(2)}</TableCell>
                                            <TableCell
                                                align="right"
                                                style={{
                                                    color: stock.change?.startsWith("-") ? "red" : "green",
                                                }}
                                            >
                                                {stock.change || "0.00%"}
                                            </TableCell>
                                        </TableRow>
                                    ))}
                                </TableBody>
                            </Table>
                        </TableContainer>
                    )}
                </Paper>
            </div>

            {/* Price Chart Section */}
            <div key="chart">
                <Paper style={{ padding: "16px", height: "100%" }}>
                    <Typography variant="h6" className="drag-handle" style={{ marginBottom: "16px", cursor: "move" }}>
                        Price Chart: {selectedSymbol}
                    </Typography>
                    {loadingChart ? (
                        <CircularProgress />
                    ) : chartError ? (
                        <Alert severity="error">{chartError}</Alert>
                    ) : (
                        <Plot
                            data={[
                                {
                                    x: chartData.dates,
                                    y: chartData.prices,
                                    type: "scatter",
                                    mode: "lines+markers",
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
                    )}
                </Paper>
            </div>
        </GridLayout>
    );
};

export default Dashboard;
