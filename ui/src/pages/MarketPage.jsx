import React from "react";
import MarketOverview from "../components/MarketOverview";
import HeatMap from "../components/HeatMap";
import EarningsCalendar from "../components/EarningsCalendar";
import NewsFeed from "../components/NewsFeed";
import { Grid } from "@mui/material";

const MarketPage = () => {
    return (
        <div className="market-page">
            <h2>Market Dashboard</h2>
            <Grid container spacing={2}>
                <Grid item xs={12} md={8}>
                    <MarketOverview />
                </Grid>
                <Grid item xs={12} md={4}>
                    <EarningsCalendar />
                </Grid>
                <Grid item xs={12}>
                    <HeatMap />
                </Grid>
                <Grid item xs={12}>
                    <NewsFeed />
                </Grid>
            </Grid>
        </div>
    );
};

export default MarketPage;
