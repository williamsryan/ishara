import React, { useEffect, useRef } from "react";
import Chart from "chart.js/auto";
import { Paper, Typography } from "@mui/material";

const StockChart = ({ data = [] }) => {
    const chartRef = useRef(null);
    let chartInstance = useRef(null);

    useEffect(() => {
        if (!data.length) return;

        if (chartInstance.current) {
            chartInstance.current.destroy(); // Destroy previous chart before re-rendering
        }

        const ctx = chartRef.current.getContext("2d");
        chartInstance.current = new Chart(ctx, {
            type: "line",
            data: {
                labels: data.map((item) => item.date),
                datasets: [
                    {
                        label: "Stock Price",
                        data: data.map((item) => item.price),
                        borderColor: "blue",
                        borderWidth: 2,
                        fill: false,
                    },
                ],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: {
                        type: "category", // Fixes 'Category is not a registered scale' error
                    },
                    y: {
                        beginAtZero: false,
                    },
                },
            },
        });

        return () => {
            if (chartInstance.current) {
                chartInstance.current.destroy();
            }
        };
    }, [data]);

    return (
        <Paper elevation={3} sx={{ padding: 2 }}>
            <Typography variant="h6">Stock Chart</Typography>
            <canvas ref={chartRef} />
        </Paper>
    );
};

export default StockChart;
