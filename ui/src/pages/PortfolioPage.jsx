import React, { useEffect, useState } from "react";
import { fetchPortfolioData } from "../utils/api";
import { DataGrid } from "@mui/x-data-grid";
import { Box, Typography, Paper } from "@mui/material";

const PortfolioPage = () => {
    const [data, setData] = useState({
        stocks: [],
        stock_prices: [],
        options: [],
        trades: [],
        portfolio: [],
        earnings: [],
        key_metrics: [],
        historical_prices: [],
        real_time_prices: [],
    });

    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const getPortfolio = async () => {
            try {
                const result = await fetchPortfolioData();
                setData(result || {
                    stocks: [],
                    stock_prices: [],
                    options: [],
                    trades: [],
                    portfolio: [],
                    earnings: [],
                    key_metrics: [],
                    historical_prices: [],
                    real_time_prices: [],
                });
                setLoading(false);
            } catch (err) {
                console.error("Error fetching portfolio data:", err);
                setError("Failed to load portfolio data.");
                setLoading(false);
            }
        };
        getPortfolio();
    }, []);

    if (loading) return <Typography>Loading...</Typography>;
    if (error) return <Typography color="error">{error}</Typography>;

    return (
        <Box sx={{ p: 3 }}>
            <Typography variant="h5" gutterBottom>
                Portfolio Overview
            </Typography>

            {/* Stocks Table */}
            <Paper sx={{ p: 2, mb: 2 }}>
                <Typography variant="h6">Stocks</Typography>
                <DataGrid
                    rows={data.stocks || []}
                    columns={[
                        { field: "symbol", headerName: "Symbol", width: 100 },
                        { field: "name", headerName: "Company", width: 200 },
                        { field: "sector", headerName: "Sector", width: 150 },
                        { field: "market_cap", headerName: "Market Cap", width: 150 },
                    ]}
                    pageSize={5}
                    autoHeight
                />
            </Paper>

            {/* Options Table */}
            <Paper sx={{ p: 2, mb: 2 }}>
                <Typography variant="h6">Options</Typography>
                <DataGrid
                    rows={data.options || []}
                    columns={[
                        { field: "symbol", headerName: "Symbol", width: 100 },
                        { field: "strike_price", headerName: "Strike Price", width: 130 },
                        { field: "expiration_date", headerName: "Expiration Date", width: 150 },
                        { field: "option_type", headerName: "Type", width: 100 },
                    ]}
                    pageSize={5}
                    autoHeight
                />
            </Paper>

            {/* Trades Table */}
            <Paper sx={{ p: 2, mb: 2 }}>
                <Typography variant="h6">Trade History</Typography>
                <DataGrid
                    rows={data.trades || []}
                    columns={[
                        { field: "symbol", headerName: "Symbol", width: 100 },
                        { field: "trade_date", headerName: "Date", width: 150 },
                        { field: "quantity", headerName: "Quantity", width: 100 },
                        { field: "price", headerName: "Price", width: 100 },
                    ]}
                    pageSize={5}
                    autoHeight
                />
            </Paper>

            {/* Portfolio Table */}
            <Paper sx={{ p: 2, mb: 2 }}>
                <Typography variant="h6">Portfolio Holdings</Typography>
                <DataGrid
                    rows={data.portfolio || []}
                    columns={[
                        { field: "symbol", headerName: "Symbol", width: 100 },
                        { field: "shares", headerName: "Shares", width: 100 },
                        { field: "average_cost", headerName: "Avg Cost", width: 100 },
                        { field: "current_price", headerName: "Current Price", width: 120 },
                        { field: "value", headerName: "Value", width: 120 },
                    ]}
                    pageSize={5}
                    autoHeight
                />
            </Paper>

            {/* Earnings Table */}
            <Paper sx={{ p: 2, mb: 2 }}>
                <Typography variant="h6">Earnings</Typography>
                <DataGrid
                    rows={data.earnings || []}
                    columns={[
                        { field: "symbol", headerName: "Symbol", width: 100 },
                        { field: "report_date", headerName: "Report Date", width: 150 },
                        { field: "actual_eps", headerName: "EPS", width: 100 },
                        { field: "consensus_eps", headerName: "Consensus EPS", width: 150 },
                    ]}
                    pageSize={5}
                    autoHeight
                />
            </Paper>

            {/* Real-Time Prices Table */}
            <Paper sx={{ p: 2, mb: 2 }}>
                <Typography variant="h6">Real-Time Prices</Typography>
                <DataGrid
                    rows={data.real_time_prices || []}
                    columns={[
                        { field: "symbol", headerName: "Symbol", width: 100 },
                        { field: "price", headerName: "Current Price", width: 150 },
                        { field: "change", headerName: "Change", width: 100 },
                        { field: "percent_change", headerName: "% Change", width: 120 },
                    ]}
                    pageSize={5}
                    autoHeight
                />
            </Paper>
        </Box>
    );
};

export default PortfolioPage;
