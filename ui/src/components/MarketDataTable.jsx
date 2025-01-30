import React from "react";
import { Table, TableHead, TableBody, TableRow, TableCell, Paper, Typography } from "@mui/material";

const MarketDataTable = () => {
    const mockData = [
        { symbol: "DIA", price: 340, change: 0.5 },
        { symbol: "SPY", price: 450, change: -0.3 },
        { symbol: "QQQ", price: 370, change: 0.2 }
    ];

    return (
        <Paper sx={{ padding: "15px", backgroundColor: "#161B22", color: "white", maxHeight: "250px", overflowY: "auto" }}>
            <Typography variant="h6">Market Overview</Typography>
            <Table>
                <TableHead>
                    <TableRow>
                        <TableCell>Symbol</TableCell>
                        <TableCell>Price</TableCell>
                        <TableCell>Change</TableCell>
                    </TableRow>
                </TableHead>
                <TableBody>
                    {mockData.map((index) => (
                        <TableRow key={index.symbol}>
                            <TableCell>{index.symbol}</TableCell>
                            <TableCell>${index.price.toFixed(2)}</TableCell>
                            <TableCell style={{ color: index.change >= 0 ? "green" : "red" }}>
                                {index.change >= 0 ? "+" : ""}
                                {index.change}%
                            </TableCell>
                        </TableRow>
                    ))}
                </TableBody>
            </Table>
        </Paper>
    );
};

export default MarketDataTable;
