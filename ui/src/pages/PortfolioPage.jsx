import React from "react";
import { Grid2, Paper, Typography, Table, TableBody, TableCell, TableContainer, TableHead, TableRow } from "@mui/material";

const PortfolioPage = () => {
    const positions = [
        { symbol: "AAPL", shares: 10, avgPrice: 140.5, currentPrice: 145.2 },
        { symbol: "GOOG", shares: 5, avgPrice: 2800.0, currentPrice: 2843.5 },
        { symbol: "TSLA", shares: 8, avgPrice: 700.0, currentPrice: 714.6 },
    ];

    return (
        <Grid2 container spacing={2} style={{ padding: "16px" }}>
            {/* Portfolio Summary */}
            <Grid2 item xs={12}>
                <Paper style={{ padding: "16px", height: "200px" }}>
                    <Typography variant="h6">Portfolio Summary</Typography>
                    <p>Total Portfolio Value: $32,400</p>
                    <p>Today's Gain/Loss: +$180 (+0.56%)</p>
                </Paper>
            </Grid2>

            {/* Open Positions */}
            <Grid2 item xs={12}>
                <TableContainer component={Paper}>
                    <Typography variant="h6" style={{ padding: "16px" }}>
                        Open Positions
                    </Typography>
                    <Table>
                        <TableHead>
                            <TableRow>
                                <TableCell>Symbol</TableCell>
                                <TableCell>Shares</TableCell>
                                <TableCell>Avg Price</TableCell>
                                <TableCell>Current Price</TableCell>
                                <TableCell>Value</TableCell>
                            </TableRow>
                        </TableHead>
                        <TableBody>
                            {positions.map((position) => (
                                <TableRow key={position.symbol}>
                                    <TableCell>{position.symbol}</TableCell>
                                    <TableCell>{position.shares}</TableCell>
                                    <TableCell>${position.avgPrice.toFixed(2)}</TableCell>
                                    <TableCell>${position.currentPrice.toFixed(2)}</TableCell>
                                    <TableCell>
                                        ${(position.shares * position.currentPrice).toFixed(2)}
                                    </TableCell>
                                </TableRow>
                            ))}
                        </TableBody>
                    </Table>
                </TableContainer>
            </Grid2>
        </Grid2>
    );
};

export default PortfolioPage;
