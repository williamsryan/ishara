import React from "react";
import { Line } from "react-chartjs-2";
import { Box, Paper } from "@mui/material";

const PriceChart = ({ data }) => {
    if (!data || Object.keys(data).length === 0) {
        return <Paper sx={{ padding: 3 }}>No Chart Data Available</Paper>;
    }

    const labels = Object.keys(data)[0] ? data[Object.keys(data)[0]].timestamps : [];
    const datasets = Object.keys(data).map((symbol) => ({
        label: symbol,
        data: data[symbol].prices,
        borderColor: "blue",
        fill: false,
    }));

    return (
        <Paper sx={{ padding: 3 }}>
            <Line data={{ labels, datasets }} />
        </Paper>
    );
};

export default PriceChart;
