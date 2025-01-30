import React, { useEffect, useState } from "react";
import { Grid, Paper, Typography, Box } from "@mui/material";
import Watchlist from "../components/Watchlist";
import StockChart from "../components/StockChart";
import NewsFeed from "../components/NewsFeed";
import api from "../utils/api"; // Ensure api.js is correctly implemented

const DashboardPage = () => {
    const [marketData, setMarketData] = useState([]);
    const [news, setNews] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        async function fetchData() {
            try {
                const [marketRes, newsRes] = await Promise.all([
                    api.get("/market"), // Replace with actual API route
                    api.get("/news"),
                ]);
                setMarketData(marketRes.data);
                setNews(newsRes.data);
            } catch (error) {
                console.error("Error fetching data:", error);
            } finally {
                setLoading(false);
            }
        }
        fetchData();
    }, []);

    return (
        <Box sx={{ flexGrow: 1, padding: 2 }}>
            <Typography variant="h4" gutterBottom>
                Dashboard
            </Typography>

            <Grid container spacing={2}>
                {/* Watchlist */}
                <Grid item xs={12} md={3}>
                    <Paper elevation={3} sx={{ padding: 2 }}>
                        <Typography variant="h6">Watchlist</Typography>
                        <Watchlist />
                    </Paper>
                </Grid>

                {/* Stock Chart */}
                <Grid item xs={12} md={9}>
                    <Paper elevation={3} sx={{ padding: 2 }}>
                        <Typography variant="h6">Portfolio Performance</Typography>
                        <StockChart />
                    </Paper>
                </Grid>

                {/* Market Data */}
                <Grid item xs={12}>
                    <Paper elevation={3} sx={{ padding: 2 }}>
                        <Typography variant="h6">Market Data</Typography>
                        {loading ? <p>Loading...</p> : <pre>{JSON.stringify(marketData, null, 2)}</pre>}
                    </Paper>
                </Grid>

                {/* Market News */}
                <Grid item xs={12}>
                    <Paper elevation={3} sx={{ padding: 2 }}>
                        <Typography variant="h6">Market News</Typography>
                        <NewsFeed />
                    </Paper>
                </Grid>
            </Grid>
        </Box>
    );
};

export default DashboardPage;
