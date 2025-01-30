import React from "react";
import { Line } from "react-chartjs-2";

const StockChart = ({ data = [] }) => {
    if (!Array.isArray(data) || data.length === 0) {
        return <div>No Data Available</div>;
    }

    const chartData = {
        labels: data.map(entry => entry.timestamp || "Unknown"),
        datasets: [
            {
                label: "Stock Price",
                data: data.map(entry => entry.price || 0),
                borderColor: "blue",
                fill: false,
            },
        ],
    };

    return (
        <div className="stock-chart">
            <Line data={chartData} />
        </div>
    );
};

export default StockChart;
