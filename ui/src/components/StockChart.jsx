import React from "react";
import { Line } from "react-chartjs-2";
import { Paper } from "@mui/material";

const StockChart = ({ data, symbol }) => {
    if (!data || !data.timestamps) return <p>Loading chart data...</p>;

    const chartData = {
        labels: data.timestamps,
        datasets: [
            {
                label: `${symbol} Price`,
                data: data.prices,
                borderColor: "rgb(75, 192, 192)",
                backgroundColor: "rgba(75, 192, 192, 0.2)",
                borderWidth: 2,
                fill: true,
                tension: 0.1,
            },
        ],
    };

    const options = {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
            x: { title: { display: true, text: "Date" } },
            y: { title: { display: true, text: "Price" } },
        },
    };

    return (
        <Paper style={{ padding: 16, height: 400 }}>
            <Line data={chartData} options={options} />
        </Paper>
    );
};

export default StockChart;
