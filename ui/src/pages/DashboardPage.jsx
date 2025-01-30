import React, { useState, useEffect } from "react";
import StockChart from "../components/StockChart";
import MarketDataTable from "../components/MarketDataTable";
import NewsFeed from "../components/NewsFeed";
import axios from "axios";

const DashboardPage = () => {
    const [marketData, setMarketData] = useState([]);
    const [news, setNews] = useState([]);

    useEffect(() => {
        axios.get("/api/stocks").then((res) => setMarketData(res.data));
        axios.get("/api/news").then((res) => setNews(res.data));
    }, []);

    return (
        <div className="dashboard">
            <h2>Market Overview</h2>
            <StockChart />
            <MarketDataTable data={marketData} />
            <NewsFeed news={news} />
        </div>
    );
};

export default DashboardPage;
