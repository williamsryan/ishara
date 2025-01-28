import React, { useState, useEffect } from "react";
import { fetchChartData } from "../utils/api";
import { Line } from "react-chartjs-2";

const ChartingPage = ({ symbol }) => {
    const [chartData, setChartData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const getChartData = async () => {
            try {
                const data = await fetchChartData(symbol);
                setChartData(data);
                setLoading(false);
            } catch (err) {
                setError("Failed to fetch chart data.");
                setLoading(false);
            }
        };
        getChartData();
    }, [symbol]);

    if (loading) return <div>Loading chart...</div>;
    if (error) return <div>{error}</div>;

    const chartConfig = {
        labels: chartData.timestamps,
        datasets: [
            {
                label: `${symbol} Price`,
                data: chartData.prices,
                borderColor: "rgba(75,192,192,1)",
                fill: false,
            },
        ],
    };

    return (
        <div>
            <h1>{symbol} Chart</h1>
            <Line data={chartConfig} />
        </div>
    );
};

export default ChartingPage;
