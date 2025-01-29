import React, { useEffect, useState } from "react";
import axios from "axios";
import { Container, Grid, Paper, Typography } from "@mui/material";
import PriceChart from "../components/PriceChart";
import Watchlist from "../components/Watchlist";
import NewsFeed from "../components/NewsFeed";
import DataTable from "../components/DataTable";

const DashboardPage = () => {
    const [chartData, setChartData] = useState(null);
    const [tableData, setTableData] = useState([]);
    const [selectedTicker, setSelectedTicker] = useState("AAPL");

    useEffect(() => {
        fetchChartData(selectedTicker);
        fetchTableData();
    }, [selectedTicker]);

    const fetchChartData = async (ticker) => {
        try {
            const response = await axios.get(`/api/charts/historical?symbol=${ticker}`);
            setChartData(response.data);
        } catch (error) {
            console.error("Error fetching chart data:", error);
        }
    };

    const fetchTableData = async () => {
        try {
            const response = await axios.get("/api/stocks/watchlist");
            setTableData(response.data);
        } catch (error) {
            console.error("Error fetching table data:", error);
        }
    };

    return (
        <Container maxWidth="xl" style={{ marginTop: "20px" }}>
            <Typography variant="h4" gutterBottom>
                Ishara Dashboard
            </Typography>

            <Grid container spacing={3}>
                {/* Price Chart */}
                <Grid item xs={12} md={8}>
                    <Paper style={{ padding: "15px", height: "400px" }}>
                        <Typography variant="h6">{selectedTicker} Price Chart</Typography>
                        {chartData ? <PriceChart data={chartData} /> : <Typography>No Data Available</Typography>}
                    </Paper>
                </Grid>

                {/* Watchlist */}
                <Grid item xs={12} md={4}>
                    <Paper style={{ padding: "15px", height: "400px" }}>
                        <Typography variant="h6">Watchlist</Typography>
                        <Watchlist />
                    </Paper>
                </Grid>

                {/* Market Data */}
                <Grid item xs={12}>
                    <Paper style={{ padding: "15px" }}>
                        <Typography variant="h6">Market Data</Typography>
                        <DataTable data={tableData} />
                    </Paper>
                </Grid>

                {/* News Feed */}
                <Grid item xs={12}>
                    <Paper style={{ padding: "15px" }}>
                        <Typography variant="h6">Market News</Typography>
                        <NewsFeed />
                    </Paper>
                </Grid>
            </Grid>
        </Container>
    );
};

export default DashboardPage;
