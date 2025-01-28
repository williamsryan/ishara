import React, { useEffect, useState } from "react";
import { DataGrid } from "@mui/x-data-grid";
import {
    LineChart,
    Line,
    XAxis,
    YAxis,
    Tooltip,
    Legend,
} from "recharts";
import GridLayout from "react-grid-layout";
import { fetchPortfolioData, fetchChartData } from "../utils/api";
import "../styles/dashboard.css";

const Dashboard = () => {
    const [positions, setPositions] = useState([]);
    const [chartData, setChartData] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchData = async () => {
            try {
                // Fetch all portfolio data
                const portfolioResponse = await fetchPortfolioData();
                setPositions(
                    portfolioResponse.stocks.map((stock, index) => ({
                        id: index,
                        symbol: stock.symbol,
                        price: stock.current_price.toFixed(2),
                        volume: stock.volume,
                    }))
                );

                // Fetch chart data for all symbols
                const chartResponse = await fetchChartData(); // No symbol passed
                const formattedChartData = Object.entries(chartResponse).map(([symbol, data]) => ({
                    symbol,
                    data: data.timestamps.map((timestamp, index) => ({
                        date: timestamp,
                        price: data.prices[index],
                    })),
                }));
                setChartData(formattedChartData);

                setLoading(false);
            } catch (err) {
                setError("Failed to load data.");
                setLoading(false);
            }
        };

        fetchData();
    }, []);

    const tableColumns = [
        { field: "symbol", headerName: "Symbol", width: 150 },
        { field: "price", headerName: "Price (USD)", width: 150 },
        { field: "volume", headerName: "Volume", width: 150 },
    ];

    const layout = [
        { i: "positions", x: 0, y: 0, w: 6, h: 8 },
        { i: "charts", x: 6, y: 0, w: 6, h: 8 },
    ];

    if (loading) return <div>Loading...</div>;
    if (error) return <div>{error}</div>;

    return (
        <GridLayout
            className="layout"
            layout={layout}
            cols={12}
            rowHeight={30}
            width={1200}
            draggableHandle=".drag-handle"
        >
            {/* Positions Table */}
            <div key="positions" className="panel">
                <h2 className="drag-handle">Positions</h2>
                <DataGrid
                    rows={positions}
                    columns={tableColumns}
                    pageSize={5}
                    rowsPerPageOptions={[5]}
                    autoHeight
                />
            </div>

            {/* Chart Data */}
            <div key="charts" className="panel">
                <h2 className="drag-handle">Stock Performance</h2>
                {chartData.map(({ symbol, data }) => (
                    <div key={symbol}>
                        <h3>{symbol}</h3>
                        <LineChart width={600} height={300} data={data}>
                            <XAxis dataKey="date" />
                            <YAxis />
                            <Tooltip />
                            <Legend />
                            <Line type="monotone" dataKey="price" stroke="#8884d8" />
                        </LineChart>
                    </div>
                ))}
            </div>
        </GridLayout>
    );
};

export default Dashboard;
