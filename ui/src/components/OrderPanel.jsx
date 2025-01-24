import React from "react";
import { Button, TextField, MenuItem, Typography } from "@mui/material";

const OrderPanel = () => {
    return (
        <div
            style={{
                backgroundColor: "#fff",
                padding: "16px",
                borderRadius: "8px",
                boxShadow: "0 2px 4px rgba(0,0,0,0.1)",
            }}
        >
            <Typography variant="h6">Place Order</Typography>
            <TextField
                label="Order Type"
                select
                fullWidth
                margin="normal"
                defaultValue="LIMIT"
            >
                <MenuItem value="LIMIT">Limit</MenuItem>
                <MenuItem value="MARKET">Market</MenuItem>
            </TextField>
            <TextField label="Quantity" type="number" fullWidth margin="normal" />
            <TextField label="Price" type="number" fullWidth margin="normal" />
            <Button variant="contained" color="primary" fullWidth>
                Submit Order
            </Button>
        </div>
    );
};

export default OrderPanel;
