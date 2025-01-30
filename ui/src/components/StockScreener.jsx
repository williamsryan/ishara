import React from "react";
import { Slider, TextField, Button } from "@mui/material";

const StockScreener = () => {
    return (
        <div className="stock-screener">
            <h3>Filter Stocks</h3>
            <TextField label="Sector" variant="outlined" size="small" />
            <Slider valueLabelDisplay="auto" min={0} max={100} />
            <Button variant="contained">Apply Filters</Button>
        </div>
    );
};

export default StockScreener;
