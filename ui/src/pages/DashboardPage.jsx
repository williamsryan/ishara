import React, { useState, useEffect } from "react";
import StockChart from "../components/StockChart";
import MarketDataTable from "../components/MarketDataTable";
import NewsFeed from "../components/NewsFeed";
import Watchlist from "../components/Watchlist";
import { Grid2, Paper } from "@mui/material";
import axios from "axios";
import Grid2Layout from "react-Grid-layout";
import "react-resizable/css/styles.css";
import "react-Grid-layout/css/styles.css";

const DashboardPage = () => {
    const [marketData, setMarketData] = useState([]);
    const [news, setNews] = useState([]);
    const [stockPrices, setStockPrices] = useState([]);

    useEffect(() => {
        axios.get("/api/stocks")
            .then((res) => setMarketData(res.data))
            .catch((err) => console.error("Error fetching stocks:", err));

        axios.get("/api/news")
            .then((res) => setNews(res.data))
            .catch((err) => console.error("Error fetching news:", err));

        axios.get("/api/charts/historical")
            .then((res) => setStockPrices(res.data))
            .catch((err) => console.error("Error fetching chart data:", err));
    }, []);

    // Define Grid2 Layout for Movable Components
    const layout = [
        { i: "chart", x: 0, y: 0, w: 3, h: 2 },
        { i: "watchlist", x: 3, y: 0, w: 1, h: 2 },
        { i: "marketdata", x: 0, y: 2, w: 4, h: 2 },
        { i: "news", x: 0, y: 4, w: 4, h: 2 },
    ];

    return (
        <Grid2 container spacing={3} sx={{ padding: 2 }}>
            <Grid2Layout
                className="react-Grid2-layout"
                layout={layout}
                cols={4}
                rowHeight={140}
                width={1200}
                draggableHandle=".drag-handle"
            >
                {/* Stock Chart */}
                <div key="chart" className="react-Grid2-item resizable-container">
                    <Paper elevation={3} sx={{ padding: 2 }}>
                        <div className="drag-handle">📈 Stock Chart</div>
                        <StockChart data={stockPrices} />
                    </Paper>
                </div>

                {/* Watchlist */}
                <div key="watchlist" className="react-Grid2-item resizable-container">
                    <Paper elevation={3} sx={{ padding: 2 }}>
                        <div className="drag-handle">📊 Watchlist</div>
                        <Watchlist />
                    </Paper>
                </div>

                {/* Market Data Table */}
                <div key="marketdata" className="react-Grid2-item resizable-container">
                    <Paper elevation={3} sx={{ padding: 2 }}>
                        <div className="drag-handle">📄 Market Data</div>
                        <MarketDataTable data={marketData} />
                    </Paper>
                </div>

                {/* News Feed */}
                <div key="news" className="react-Grid2-item resizable-container">
                    <Paper elevation={3} sx={{ padding: 2 }}>
                        <div className="drag-handle">📰 Market News</div>
                        <NewsFeed news={news} />
                    </Paper>
                </div>
            </Grid2Layout>
        </Grid2>
    );
};

export default DashboardPage;
