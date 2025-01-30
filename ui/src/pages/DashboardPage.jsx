import React, { useState, useEffect } from "react";
import { Box, Paper, Typography } from "@mui/material";
import GridLayout from "react-grid-layout";
import PriceChart from "../components/PriceChart";
import Watchlist from "../components/Watchlist";
import DataTable from "../components/DataTable";
import NewsFeed from "../components/NewsFeed";
import PortfolioOverview from "../components/PortfolioOverview";
import OrderPanel from "../components/OrderPanel";
import "react-grid-layout/css/styles.css";
import "react-resizable/css/styles.css";

const DashboardPage = ({ sidebarOpen }) => {
    const [layout, setLayout] = useState([
        { i: "chart", x: 0, y: 0, w: 6, h: 4 },
        { i: "watchlist", x: 6, y: 0, w: 3, h: 4 },
        { i: "marketdata", x: 9, y: 0, w: 3, h: 4 },
        { i: "news", x: 0, y: 4, w: 12, h: 3 },
        { i: "portfolio", x: 0, y: 7, w: 6, h: 3 },
        { i: "orderform", x: 6, y: 7, w: 6, h: 3 },
    ]);

    useEffect(() => {
        setLayout((prevLayout) =>
            prevLayout.map((item) => ({
                ...item,
                x: item.x,
            }))
        );
    }, [sidebarOpen]);

    return (
        <Box
            sx={{
                flexGrow: 1,
                transition: "margin 0.3s ease-in-out",
                padding: "10px",
                marginLeft: sidebarOpen ? "250px" : "60px",
                width: sidebarOpen ? "calc(100% - 250px)" : "calc(100% - 60px)",
            }}
        >
            <GridLayout
                className="layout"
                layout={layout}
                cols={12}
                rowHeight={80}
                width={window.innerWidth - (sidebarOpen ? 250 : 80)}
                draggableHandle=".drag-handle"
                isResizable
                isDraggable
                onLayoutChange={(newLayout) => setLayout(newLayout)}
                compactType="horizontal"
            >
                {/* Stock Chart */}
                <div key="chart">
                    <Paper elevation={3} sx={{ padding: "10px", height: "100%" }}>
                        <Typography variant="h6" className="drag-handle">
                            SPY Price Chart
                        </Typography>
                        <PriceChart symbol="SPY" />
                    </Paper>
                </div>

                {/* Watchlist */}
                <div key="watchlist">
                    <Paper elevation={3} sx={{ padding: "10px", height: "100%" }}>
                        <Typography variant="h6" className="drag-handle">
                            Watchlist
                        </Typography>
                        <Watchlist />
                    </Paper>
                </div>

                {/* Market Data */}
                <div key="marketdata">
                    <Paper elevation={3} sx={{ padding: "10px", height: "100%" }}>
                        <Typography variant="h6" className="drag-handle">
                            Market Data
                        </Typography>
                        <DataTable />
                    </Paper>
                </div>

                {/* Market News */}
                <div key="news">
                    <Paper elevation={3} sx={{ padding: "10px", height: "100%" }}>
                        <Typography variant="h6" className="drag-handle">
                            Market News
                        </Typography>
                        <NewsFeed />
                    </Paper>
                </div>

                {/* Portfolio Overview */}
                <div key="portfolio">
                    <Paper elevation={3} sx={{ padding: "10px", height: "100%" }}>
                        <Typography variant="h6" className="drag-handle">
                            Portfolio Overview
                        </Typography>
                        <PortfolioOverview />
                    </Paper>
                </div>

                {/* Order Form */}
                <div key="orderform">
                    <Paper elevation={3} sx={{ padding: "10px", height: "100%" }}>
                        <Typography variant="h6" className="drag-handle">
                            Place an Order
                        </Typography>
                        <OrderPanel />
                    </Paper>
                </div>
            </GridLayout>
        </Box>
    );
};

export default DashboardPage;
