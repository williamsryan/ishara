import React from "react";
import { Line } from "react-chartjs-2";
import "chart.js/auto";

const PriceChart = ({ data }) => {
    if (!data || !data.timestamps || !data.prices) {
        return <p>No Chart Data Available</p>;
    }

    const chartData = {
        labels: data.timestamps,
        datasets: [
            {
                label: "Stock Price",
                data: data.prices,
                borderColor: "rgba(75,192,192,1)",
                backgroundColor: "rgba(75,192,192,0.2)",
                fill: true,
                tension: 0.3,
            },
        ],
    };

    const options = {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
            x: {
                grid: { display: false },
            },
            y: {
                beginAtZero: false,
                grid: { color: "rgba(200,200,200,0.2)" },
            },
        },
    };

    return <div style={{ height: "350px", width: "100%" }}><Line data={chartData} options={options} /></div>;
};

export default PriceChart;
