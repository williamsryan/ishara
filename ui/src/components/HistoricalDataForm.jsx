import React, { useState } from "react";
import { TextField, Button, MenuItem, Paper, Typography } from "@mui/material";
import { DatePicker } from "@mui/x-date-pickers/DatePicker";
import axios from "axios";
import { DataGrid } from "@mui/x-data-grid";

const availableTickers = ["AAPL", "MSFT", "TSLA", "GOOGL", "AMZN", "NVDA"];

const HistoricalDataForm = () => {
    const [selectedTickers, setSelectedTickers] = useState(["AAPL"]);
    const [startDate, setStartDate] = useState(null);
    const [endDate, setEndDate] = useState(null);
    const [historicalData, setHistoricalData] = useState([]);
    const [loading, setLoading] = useState(false);

    const handleFetchData = async () => {
        if (!startDate || !endDate || selectedTickers.length === 0) {
            alert("Please select tickers and date range.");
            return;
        }

        setLoading(true);

        try {
            const symbols = selectedTickers.join(",");
            const response = await axios.get(
                `http://localhost:1337/api/charts/historical/`,
                {
                    params: {
                        symbols,
                        start_date: startDate.format("YYYY-MM-DD"),
                        end_date: endDate.format("YYYY-MM-DD"),
                    },
                }
            );

            setHistoricalData(response.data);
        } catch (error) {
            console.error("Error fetching historical data:", error);
            alert("Failed to fetch historical data.");
        }

        setLoading(false);
    };

    const columns = [
        { field: "date", headerName: "Date", width: 120 },
        { field: "symbol", headerName: "Symbol", width: 100 },
        { field: "price", headerName: "Price", width: 120 },
    ];

    const rows = [];
    Object.entries(historicalData).forEach(([symbol, data]) => {
        data.timestamps.forEach((date, index) => {
            rows.push({ id: `${symbol}-${date}`, date, symbol, price: data.prices[index] });
        });
    });

    return (
        <Paper elevation={3} style={{ padding: 16, marginTop: 16 }}>
            <Typography variant="h6">Fetch Historical Data</Typography>

            {/* Ticker Selection */}
            <TextField
                select
                label="Select Tickers"
                value={selectedTickers}
                onChange={(e) => setSelectedTickers(e.target.value.split(","))}
                fullWidth
                SelectProps={{
                    multiple: true,
                }}
                style={{ marginTop: 16 }}
            >
                {availableTickers.map((ticker) => (
                    <MenuItem key={ticker} value={ticker}>
                        {ticker}
                    </MenuItem>
                ))}
            </TextField>

            {/* Date Pickers */}
            <DatePicker
                label="Start Date"
                value={startDate}
                onChange={(newValue) => setStartDate(newValue)}
                style={{ marginTop: 16, marginRight: 8 }}
            />
            <DatePicker
                label="End Date"
                value={endDate}
                onChange={(newValue) => setEndDate(newValue)}
                style={{ marginTop: 16 }}
            />

            {/* Fetch Data Button */}
            <Button
                variant="contained"
                color="primary"
                onClick={handleFetchData}
                disabled={loading}
                style={{ marginTop: 16 }}
            >
                {loading ? "Fetching..." : "Fetch Data"}
            </Button>

            {/* Data Table */}
            {historicalData && Object.keys(historicalData).length > 0 && (
                <div style={{ height: 400, width: "100%", marginTop: 16 }}>
                    <DataGrid rows={rows} columns={columns} />
                </div>
            )}
        </Paper>
    );
};

export default HistoricalDataForm;
