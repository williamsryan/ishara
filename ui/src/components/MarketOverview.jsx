import React, { useEffect, useState } from "react";
import axios from "axios";
import { Card, CardContent, Typography, Grid } from "@mui/material";

const MarketOverview = () => {
    const [marketData, setMarketData] = useState([]);

    useEffect(() => {
        axios.get("/api/market").then((res) => setMarketData(res.data));
    }, []);

    return (
        <Card className="market-overview">
            <CardContent>
                <Typography variant="h5">Market Overview</Typography>
                <Grid container spacing={2}>
                    {marketData.map((index, i) => (
                        <Grid item xs={4} key={i}>
                            <Typography variant="h6">{index.name}</Typography>
                            <Typography variant="body1">{index.price} ({index.change}%)</Typography>
                        </Grid>
                    ))}
                </Grid>
            </CardContent>
        </Card>
    );
};

export default MarketOverview;
