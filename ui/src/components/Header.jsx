import React, { useState } from "react";
import { AppBar, Toolbar, TextField, Button, Box } from "@mui/material";
import axios from "axios";

const Header = ({ onSearch }) => {
    const [ticker, setTicker] = useState("");
    const [startDate, setStartDate] = useState("");
    const [endDate, setEndDate] = useState("");

    const handleSearch = () => {
        if (ticker && startDate && endDate) {
            axios.get(`/api/charts/historical?ticker=${ticker}&start=${startDate}&end=${endDate}`)
                .then((res) => onSearch(res.data))
                .catch((err) => console.error("Error fetching historical data:", err));
        }
    };

    return (
        <AppBar position="static">
            <Toolbar>
                <Box sx={{ flexGrow: 1 }}>
                    <TextField label="Search Ticker" variant="outlined" size="small"
                        value={ticker} onChange={(e) => setTicker(e.target.value)} sx={{ marginRight: 1 }} />
                    <TextField type="date" size="small" onChange={(e) => setStartDate(e.target.value)} sx={{ marginRight: 1 }} />
                    <TextField type="date" size="small" onChange={(e) => setEndDate(e.target.value)} sx={{ marginRight: 1 }} />
                    <Button variant="contained" onClick={handleSearch}>Get Data</Button>
                </Box>
            </Toolbar>
        </AppBar>
    );
};

export default Header;
