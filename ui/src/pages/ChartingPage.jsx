import React, { useState } from "react";
import StockChart from "../components/StockChart";
import { TextField, Button } from "@mui/material";

const ChartingPage = () => {
    const [ticker, setTicker] = useState("");

    return (
        <div className="charting-page">
            <h2>Advanced Charting</h2>
            <div className="chart-input">
                <TextField
                    label="Enter Ticker"
                    variant="outlined"
                    size="small"
                    value={ticker}
                    onChange={(e) => setTicker(e.target.value)}
                />
                <Button variant="contained">Load Chart</Button>
            </div>
            <StockChart symbol={ticker} />
        </div>
    );
};

export default ChartingPage;
