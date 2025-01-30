import React, { useState, useEffect } from "react";
import { Box, Paper, Typography, IconButton } from "@mui/material";
import Grid2 from "@mui/material/Grid"; 
import CloseIcon from "@mui/icons-material/Close";
import { Responsive, WidthProvider } from "react-grid-layout";

import PriceChart from "../components/PriceChart";
import Watchlist from "../components/Watchlist";
import DataTable from "../components/DataTable";
import NewsFeed from "../components/NewsFeed";
import PortfolioOverview from "../components/PortfolioOverview";
import OrderPanel from "../components/OrderPanel";

import "react-grid-layout/css/styles.css";
import "react-resizable/css/styles.css";

const ResponsiveGridLayout = WidthProvider(Responsive);

const DashboardPage = ({ sidebarOpen }) => {
    const [layout, setLayout] = useState([
        { i: "chart", x: 0, y: 0, w: 6, h: 4 },
        { i: "watchlist", x: 6, y: 0, w: 3, h: 4 },
        { i: "marketdata", x: 9, y: 0, w: 3, h: 4 },
        { i: "news", x: 0, y: 4, w: 12, h: 2 },  
        { i: "portfolio", x: 0, y: 6, w: 6, h: 3 },
        { i: "orderform", x: 6, y: 6, w: 6, h: 3 },
    ]);

    // Handle Removing Components
    const handleDelete = (key) => {
        setLayout((prevLayout) => prevLayout.filter((item) => item.i !== key));
    };

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
                display: "flex",
                flexDirection: "column",
                height: "100vh",
                flexGrow: 1,
                transition: "margin 0.3s ease-in-out",
                padding: "10px",
                marginLeft: sidebarOpen ? "250px" : "60px",
                width: sidebarOpen ? "calc(100% - 250px)" : "calc(100% - 60px)",
            }}
        >
            {/* Responsive Grid Layout */}
            <ResponsiveGridLayout
                className="layout"
                layouts={{ lg: layout, md: layout, sm: layout }}
                breakpoints={{ lg: 1200, md: 996, sm: 768 }}
                cols={{ lg: 12, md: 12, sm: 12 }}
                rowHeight={80}
                draggableHandle=".drag-handle"
                isResizable
                isDraggable
                onLayoutChange={(newLayout) => setLayout(newLayout)}
                compactType="horizontal"
            >
                {layout.map((item) => (
                    <Grid2 key={item.i} xs={12} sm={6} md={4} lg={3}>
                        <Paper elevation={3} sx={{ padding: "10px", height: "100%", position: "relative" }}>
                            {/* Delete Button */}
                            <IconButton
                                onClick={() => handleDelete(item.i)}
                                sx={{ position: "absolute", top: 5, right: 5 }}
                                size="small"
                            >
                                <CloseIcon fontSize="small" />
                            </IconButton>

                            {/* Title */}
                            <Typography variant="h6" className="drag-handle">
                                {item.i === "chart" && "SPY Price Chart"}
                                {item.i === "watchlist" && "Watchlist"}
                                {item.i === "marketdata" && "Market Data"}
                                {item.i === "news" && "Market News"}
                                {item.i === "portfolio" && "Portfolio Overview"}
                                {item.i === "orderform" && "Place an Order"}
                            </Typography>

                            {/* Component Rendering */}
                            {item.i === "chart" && <PriceChart symbol="SPY" />}
                            {item.i === "watchlist" && <Watchlist />}
                            {item.i === "marketdata" && <DataTable />}
                            {item.i === "news" && <NewsFeed />}
                            {item.i === "portfolio" && <PortfolioOverview />}
                            {item.i === "orderform" && <OrderPanel />}
                        </Paper>
                    </Grid2>
                ))}
            </ResponsiveGridLayout>
        </Box>
    );
};

export default DashboardPage;
