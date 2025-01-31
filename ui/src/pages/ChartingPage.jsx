import React, { useState, useEffect } from "react";
import { fetchHistoricalData } from "../utils/api";
import { TextField, Button, Grid2, Paper, Tabs, Tab } from "@mui/material";
import StockChart from "../components/StockChart";

const ChartingPage = () => {
    const [ticker, setTicker] = useState("AAPL");
    const [startDate, setStartDate] = useState("2024-01-01");
    const [endDate, setEndDate] = useState("2024-02-01");
    const [historicalData, setHistoricalData] = useState(null);
    const [tabIndex, setTabIndex] = useState(0); // 0 = Live, 1 = Historical

    const fetchHistorical = async () => {
        try {
            const data = await fetchHistoricalData(ticker, startDate, endDate);
            setHistoricalData(data);
        } catch (error) {
            console.error("Error fetching historical data", error);
        }
    };

    return (
        <Grid2 container spacing={2}>
            <Grid2 item xs={12}>
                <Paper>
                    <Tabs value={tabIndex} onChange={(_, newIndex) => setTabIndex(newIndex)} centered>
                        <Tab label="Live Chart" />
                        <Tab label="Historical Data" />
                    </Tabs>
                </Paper>
            </Grid2>

            {/* Historical Data Input Fields */}
            {tabIndex === 1 && (
                <Grid2 item xs={12} md={6}>
                    <Paper style={{ padding: 16 }}>
                        <TextField
                            label="Stock Ticker"
                            value={ticker}
                            onChange={(e) => setTicker(e.target.value.toUpperCase())}
                            fullWidth
                            variant="outlined"
                            style={{ marginBottom: 10 }}
                        />
                        <TextField
                            label="Start Date"
                            type="date"
                            value={startDate}
                            onChange={(e) => setStartDate(e.target.value)}
                            fullWidth
                            InputLabelProps={{ shrink: true }}
                            style={{ marginBottom: 10 }}
                        />
                        <TextField
                            label="End Date"
                            type="date"
                            value={endDate}
                            onChange={(e) => setEndDate(e.target.value)}
                            fullWidth
                            InputLabelProps={{ shrink: true }}
                            style={{ marginBottom: 10 }}
                        />
                        <Button variant="contained" color="primary" fullWidth onClick={fetchHistorical}>
                            Fetch Historical Data
                        </Button>
                    </Paper>
                </Grid2>
            )}

            {/* Display Stock Chart (Live or Historical) */}
            <Grid2 item xs={12}>
                <Paper>
                    <StockChart data={tabIndex === 0 ? null : historicalData} symbol={ticker} />
                </Paper>
            </Grid2>
        </Grid2>
    );
};

export default ChartingPage;
