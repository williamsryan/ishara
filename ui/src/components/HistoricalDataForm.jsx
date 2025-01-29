import React, { useState } from "react";
import { TextField, Button, Grid } from "@mui/material";

const HistoricalDataForm = ({ onSearch }) => {
    const [ticker, setTicker] = useState("");
    const [startDate, setStartDate] = useState("");
    const [endDate, setEndDate] = useState("");

    const handleSearch = () => {
        if (!ticker) return;
        onSearch(ticker);
    };

    return (
        <Grid container spacing={2} style={{ marginBottom: "20px" }}>
            <Grid item xs={4}>
                <TextField
                    label="Search Ticker"
                    variant="outlined"
                    fullWidth
                    value={ticker}
                    onChange={(e) => setTicker(e.target.value)}
                />
            </Grid>
            <Grid item xs={3}>
                <TextField
                    label="Start Date"
                    type="date"
                    InputLabelProps={{ shrink: true }}
                    fullWidth
                    value={startDate}
                    onChange={(e) => setStartDate(e.target.value)}
                />
            </Grid>
            <Grid item xs={3}>
                <TextField
                    label="End Date"
                    type="date"
                    InputLabelProps={{ shrink: true }}
                    fullWidth
                    value={endDate}
                    onChange={(e) => setEndDate(e.target.value)}
                />
            </Grid>
            <Grid item xs={2}>
                <Button variant="contained" color="primary" fullWidth onClick={handleSearch}>
                    Get Data
                </Button>
            </Grid>
        </Grid>
    );
};

export default HistoricalDataForm;
