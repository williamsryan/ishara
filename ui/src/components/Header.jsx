import React, { useState } from "react";
import { fetchHistoricalData } from "../utils/api";

const Header = ({ setHistoricalData }) => {
    const [symbols, setSymbols] = useState("");
    const [startDate, setStartDate] = useState("");
    const [endDate, setEndDate] = useState("");
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const handleFetchData = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError(null);

        try {
            const response = await fetchHistoricalData(symbols, startDate, endDate);
            setHistoricalData(response); // Pass data to the parent component via props
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
                <input
                    type="text"
                    placeholder="Symbols (e.g., AAPL, MSFT)"
                    value={symbols}
                    onChange={(e) => setSymbols(e.target.value)}
                    required
                />
                <input
                    type="date"
                    value={startDate}
                    onChange={(e) => setStartDate(e.target.value)}
                    required
                />
                <input
                    type="date"
                    value={endDate}
                    onChange={(e) => setEndDate(e.target.value)}
                    required
                />
                <button type="submit" disabled={loading}>
                    {loading ? "Fetching..." : "Fetch Data"}
                </button>
                {error && <span className="error-message">{error}</span>}
            </form>
        </header>
    );
};

export default Header;
