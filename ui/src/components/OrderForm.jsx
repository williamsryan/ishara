import React, { useState } from "react";
import { TextField, MenuItem, Button, Grid } from "@mui/material";

const OrderForm = () => {
    const [orderType, setOrderType] = useState("LIMIT");
    const [quantity, setQuantity] = useState(1);
    const [limitPrice, setLimitPrice] = useState("");
    const [side, setSide] = useState("BUY");

    const handleSubmit = () => {
        console.log("Order Placed:", { side, orderType, quantity, limitPrice });
    };

    return (
        <div className="order-form">
            <h3>Place Order</h3>
            <Grid container spacing={2}>
                <Grid item xs={6}>
                    <TextField
                        select
                        label="Order Type"
                        fullWidth
                        value={orderType}
                        onChange={(e) => setOrderType(e.target.value)}
                    >
                        <MenuItem value="LIMIT">Limit</MenuItem>
                        <MenuItem value="MARKET">Market</MenuItem>
                        <MenuItem value="STOP">Stop</MenuItem>
                    </TextField>
                </Grid>
                <Grid item xs={6}>
                    <TextField
                        select
                        label="Side"
                        fullWidth
                        value={side}
                        onChange={(e) => setSide(e.target.value)}
                    >
                        <MenuItem value="BUY">Buy</MenuItem>
                        <MenuItem value="SELL">Sell</MenuItem>
                    </TextField>
                </Grid>
                <Grid item xs={6}>
                    <TextField
                        label="Quantity"
                        type="number"
                        fullWidth
                        value={quantity}
                        onChange={(e) => setQuantity(e.target.value)}
                    />
                </Grid>
                <Grid item xs={6}>
                    <TextField
                        label="Limit Price"
                        type="number"
                        fullWidth
                        value={limitPrice}
                        onChange={(e) => setLimitPrice(e.target.value)}
                        disabled={orderType !== "LIMIT"}
                    />
                </Grid>
                <Grid item xs={12}>
                    <Button variant="contained" color="primary" fullWidth onClick={handleSubmit}>
                        Submit Order
                    </Button>
                </Grid>
            </Grid>
        </div>
    );
};

export default OrderForm;
