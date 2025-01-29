import React, { useState } from "react";
import { fetchHistoricalData, searchStockSymbols } from "../utils/api";
import { Autocomplete, TextField } from "@mui/material";

const Header = ({ setHistoricalData }) => {
    const [searchTerm, setSearchTerm] = useState("");
    const [selectedSymbol, setSelectedSymbol] = useState(null);
    const [suggestions, setSuggestions] = useState([]);
    const [startDate, setStartDate] = useState("");
    const [endDate, setEndDate] = useState("");
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const handleSearchChange = async (event, value) => {
        setSearchTerm(value);
        if (value.length > 1) {
            const results = await searchStockSymbols(value);
            setSuggestions(results);
        } else {
            setSuggestions([]);
        }
    };

    const handleSymbolSelect = (event, newValue) => {
        setSelectedSymbol(newValue);
    };

    const handleFetchData = async (e) => {
        e.preventDefault();
        if (!selectedSymbol) {
            setError("Please select a valid stock symbol.");
            return;
        }
        setLoading(true);
        setError(null);

        try {
            const response = await fetchHistoricalData(selectedSymbol, startDate, endDate);
            setHistoricalData(response);
        } catch (err) {
            setError("Failed to fetch historical data.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <header className="app-header">
            <h1>Ishara Dashboard</h1>
            <form onSubmit={handleFetchData} className="historical-data-form">
                {/* Ticker Autocomplete Search */}
                <Autocomplete
                    options={suggestions}
                    getOptionLabel={(option) => option.symbol}
                    onInputChange={handleSearchChange}
                    onChange={handleSymbolSelect}
                    renderInput={(params) => (
                        <TextField {...params} label="Search Ticker" variant="outlined" size="small" />
                    )}
                    style={{ width: 200, marginRight: "10px" }}
                />

                {/* Date Pickers */}
                <TextField
                    type="date"
                    value={startDate}
                    onChange={(e) => setStartDate(e.target.value)}
                    size="small"
                    variant="outlined"
                    style={{ marginRight: "10px" }}
                />
                <TextField
                    type="date"
                    value={endDate}
                    onChange={(e) => setEndDate(e.target.value)}
                    size="small"
                    variant="outlined"
                    style={{ marginRight: "10px" }}
                />

                <button type="submit" disabled={loading}>
                    {loading ? "Fetching..." : "Get Data"}
                </button>
                {error && <span className="error-message">{error}</span>}
            </form>
        </header>
    );
};

export default Header;
