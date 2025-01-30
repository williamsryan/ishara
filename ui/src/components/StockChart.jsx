import React from "react";
import { Line } from "react-chartjs-2";

const StockChart = ({ data }) => {
    const chartData = {
        labels: data.map((point) => point.timestamp),
        datasets: [
            {
                label: "Stock Price",
                data: data.map((point) => point.price),
                borderColor: "#0071db",
                backgroundColor: "rgba(0, 113, 219, 0.2)",
                fill: true,
            },
        ],
    };

    return (
        <div className="chart-container">
            <Line data={chartData} />
        </div>
    );
};

export default StockChart;
