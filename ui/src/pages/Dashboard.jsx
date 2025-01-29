import React, { useState } from "react";
import { DataGrid } from "@mui/x-data-grid";
import { LineChart, Line, XAxis, YAxis, Tooltip, Legend } from "recharts";
import GridLayout from "react-grid-layout";
import "../styles/dashboard.css";
import Header from "../components/Header";

const Dashboard = () => {
    const [historicalData, setHistoricalData] = useState({});

    const layout = [
        { i: "positions", x: 0, y: 0, w: 6, h: 8 },
        { i: "charts", x: 6, y: 0, w: 6, h: 8 },
    ];

    return (
        <div>
            <Header setHistoricalData={setHistoricalData} />
            <GridLayout className="layout" layout={layout} cols={12} rowHeight={30} width={1200}>
                {/* Chart Data */}
                <div key="charts" className="panel">
                    <h2 className="drag-handle">Stock Performance</h2>
                    {Object.entries(historicalData).map(([symbol, data]) => (
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
        </div>
    );
};

export default Dashboard;
