import React, { useState } from "react";
import { LineChart, Line, XAxis, YAxis, Tooltip, Legend } from "recharts";

const HistoricalDataForm = () => {
    const [symbols, setSymbols] = useState("");
    const [startDate, setStartDate] = useState("");
    const [endDate, setEndDate] = useState("");
    const [chartData, setChartData] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError(null);

        try {
            const response = await fetch(
                `/api/charts/historical/?symbols=${symbols}&start_date=${startDate}&end_date=${endDate}`
            );
            if (!response.ok) throw new Error("Failed to fetch historical data.");

            const data = await response.json();

            // Transform response for chart rendering
            const formattedData = Object.entries(data).flatMap(([symbol, symbolData]) =>
                symbolData.timestamps.map((timestamp, index) => ({
                    symbol,
                    date: timestamp,
                    price: symbolData.prices[index],
                }))
            );

            setChartData(formattedData);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div>
            <h2>Fetch Historical Data</h2>
            <form onSubmit={handleSubmit}>
                <label>
                    Tickers (comma-separated):
                    <input
                        type="text"
                        value={symbols}
                        onChange={(e) => setSymbols(e.target.value)}
                        required
                    />
                </label>
                <label>
                    Start Date:
                    <input
                        type="date"
                        value={startDate}
                        onChange={(e) => setStartDate(e.target.value)}
                        required
                    />
                </label>
                <label>
                    End Date:
                    <input
                        type="date"
                        value={endDate}
                        onChange={(e) => setEndDate(e.target.value)}
                        required
                    />
                </label>
                <button type="submit">Fetch Data</button>
            </form>

            {loading && <p>Loading...</p>}
            {error && <p style={{ color: "red" }}>{error}</p>}

            {chartData.length > 0 && (
                <div>
                    <h3>Historical Data</h3>
                    <LineChart width={800} height={400} data={chartData}>
                        <XAxis dataKey="date" />
                        <YAxis />
                        <Tooltip />
                        <Legend />
                        <Line type="monotone" dataKey="price" stroke="#8884d8" />
                    </LineChart>
                </div>
            )}
        </div>
    );
};

export default HistoricalDataForm;
