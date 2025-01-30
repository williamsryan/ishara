import React, { useState, useEffect } from "react";
import { Paper, Typography, Table, TableBody, TableCell, TableContainer, TableHead, TableRow } from "@mui/material";
import axios from "axios";

const PortfolioOverview = () => {
    const [portfolio, setPortfolio] = useState([]);

    useEffect(() => {
        // Fetch portfolio data from API
        axios.get("/api/portfolio")
            .then((response) => {
                setPortfolio(response.data);
            })
            .catch((error) => {
                console.error("Error fetching portfolio data:", error);
            });
    }, []);

    return (
        <Paper elevation={3} sx={{ padding: "10px", height: "100%" }}>
            {/* <Typography variant="h6">Portfolio Overview</Typography> */}
            <TableContainer>
                <Table size="small">
                    <TableHead>
                        <TableRow>
                            <TableCell>Symbol</TableCell>
                            <TableCell>Shares</TableCell>
                            <TableCell>Average Cost</TableCell>
                            <TableCell>Current Price</TableCell>
                            <TableCell>Value</TableCell>
                            <TableCell>Change</TableCell>
                        </TableRow>
                    </TableHead>
                    <TableBody>
                        {portfolio.length > 0 ? (
                            portfolio.map((stock) => (
                                <TableRow key={stock.symbol}>
                                    <TableCell>{stock.symbol}</TableCell>
                                    <TableCell>{stock.shares}</TableCell>
                                    <TableCell>${stock.avgCost.toFixed(2)}</TableCell>
                                    <TableCell>${stock.currentPrice.toFixed(2)}</TableCell>
                                    <TableCell>${(stock.shares * stock.currentPrice).toFixed(2)}</TableCell>
                                    <TableCell
                                        sx={{
                                            color: stock.change >= 0 ? "green" : "red",
                                            fontWeight: "bold",
                                        }}
                                    >
                                        {stock.change.toFixed(2)}%
                                    </TableCell>
                                </TableRow>
                            ))
                        ) : (
                            <TableRow>
                                <TableCell colSpan={6} align="center">
                                    No portfolio data available
                                </TableCell>
                            </TableRow>
                        )}
                    </TableBody>
                </Table>
            </TableContainer>
        </Paper>
    );
};

export default PortfolioOverview;
