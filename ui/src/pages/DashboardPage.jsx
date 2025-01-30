import React, { useState, useEffect } from "react";
import StockChart from "../components/StockChart";
import MarketDataTable from "../components/MarketDataTable";
import NewsFeed from "../components/NewsFeed";
import Watchlist from "../components/Watchlist";
import { Grid, Paper } from "@mui/material";
import axios from "axios";

const DashboardPage = () => {
    const [marketData, setMarketData] = useState([]);
    const [news, setNews] = useState([]);
    const [stockPrices, setStockPrices] = useState([]);

    useEffect(() => {
        axios.get("/api/stocks")
            .then((res) => setMarketData(res.data))
            .catch((err) => console.error("Error fetching stocks:", err));

        axios.get("/api/news")
            .then((res) => setNews(res.data))
            .catch((err) => console.error("Error fetching news:", err));

        axios.get("/api/charts/historical")
            .then((res) => setStockPrices(res.data))
            .catch((err) => console.error("Error fetching chart data:", err));
    }, []);

    return (
        <Grid container spacing={3} sx={{ padding: 2 }}>
            {/* Stock Chart */}
            <Grid item xs={12} md={8}>
                <Paper elevation={3} sx={{ padding: 2 }}>
                    <StockChart data={stockPrices} />
                </Paper>
            </Grid>

            {/* Watchlist */}
            <Grid item xs={12} md={4}>
                <Paper elevation={3} sx={{ padding: 2 }}>
                    <Watchlist />
                </Paper>
            </Grid>

            {/* Market Data Table */}
            <Grid item xs={12}>
                <Paper elevation={3} sx={{ padding: 2 }}>
                    <MarketDataTable data={marketData} />
                </Paper>
            </Grid>

            {/* News Feed */}
            <Grid item xs={12}>
                <Paper elevation={3} sx={{ padding: 2 }}>
                    <NewsFeed news={news} />
                </Paper>
            </Grid>
        </Grid>
    );
};

export default DashboardPage;
