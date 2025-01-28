import React, { useState, useEffect, useRef } from "react";
import { Line } from "react-chartjs-2";
import { fetchChartData } from "../utils/api";
import { Chart } from "chart.js/auto";

const ChartingPage = ({ symbol = "AAPL" }) => {
    const [chartData, setChartData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const chartRef = useRef(null);

    useEffect(() => {
        const getChartData = async () => {
            try {
                const data = await fetchChartData(symbol);

                if (chartRef.current) {
                    chartRef.current.destroy(); // Destroy previous instance
                }

                setChartData({
                    labels: data.timestamps,
                    datasets: [
                        {
                            label: `${symbol} Price`,
                            data: data.prices,
                            borderColor: "rgba(75,192,192,1)",
                            fill: false,
                        },
                    ],
                });

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

    return (
        <div>
            <h1>{symbol} Chart</h1>
            <Line ref={chartRef} data={chartData} />
        </div>
    );
};

export default ChartingPage;
