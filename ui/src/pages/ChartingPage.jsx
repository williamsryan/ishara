import React, { useState, useEffect } from "react";
import { fetchHistoricalData } from "../utils/api";
import { Grid, Paper, TextField, Button, Tabs, Tab, CircularProgress } from "@mui/material";
import StockChart from "../components/StockChart";
import "../styles/ChartingPage.css";

const ChartingPage = () => {
    const [ticker, setTicker] = useState("AAPL");
    const [startDate, setStartDate] = useState("2024-01-01");
    const [endDate, setEndDate] = useState("2024-02-01");
    const [historicalData, setHistoricalData] = useState(null);
    const [tabIndex, setTabIndex] = useState(0);
    const [loading, setLoading] = useState(false);

    const fetchHistorical = async () => {
        setLoading(true);
        try {
            const data = await fetchHistoricalData(ticker, startDate, endDate);
            setHistoricalData(data);
        } catch (error) {
            console.error("Error fetching historical data", error);
        }
        setLoading(false);
    };

    return (
        <Grid container spacing={2} className="charting-page">
            <Grid item xs={12}>
                <Paper className="charting-widget">
                    <Tabs value={tabIndex} onChange={(_, newIndex) => setTabIndex(newIndex)} centered>
                        <Tab label="Live Chart" />
                        <Tab label="Historical Data" />
                    </Tabs>
                </Paper>
            </Grid>

            {tabIndex === 1 && (
                <Grid item xs={12} md={4}>
                    <Paper className="charting-widget">
                        <TextField
                            label="Stock Ticker"
                            value={ticker}
                            onChange={(e) => setTicker(e.target.value.toUpperCase())}
                            fullWidth
                            variant="outlined"
                        />
                        <TextField
                            label="Start Date"
                            type="date"
                            value={startDate}
                            onChange={(e) => setStartDate(e.target.value)}
                            fullWidth
                            InputLabelProps={{ shrink: true }}
                        />
                        <TextField
                            label="End Date"
                            type="date"
                            value={endDate}
                            onChange={(e) => setEndDate(e.target.value)}
                            fullWidth
                            InputLabelProps={{ shrink: true }}
                        />
                        <Button variant="contained" color="primary" onClick={fetchHistorical}>
                            Fetch Historical Data
                        </Button>
                    </Paper>
                </Grid>
            )}

            <Grid item xs={12} md={8}>
                <Paper className="charting-widget chart-container">
                    {loading ? <CircularProgress /> : <StockChart data={tabIndex === 1 ? historicalData : null} symbol={ticker} />}
                </Paper>
            </Grid>
        </Grid>
    );
};

export default ChartingPage;
