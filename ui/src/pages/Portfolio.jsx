import React from "react";
import { Paper, Typography, Table, TableBody, TableCell, TableContainer, TableHead, TableRow } from "@mui/material";
import GridLayout from "react-grid-layout";
import "react-grid-layout/css/styles.css";
import "react-resizable/css/styles.css";

const Portfolio = () => {
    const positions = [
        { symbol: "AAPL", shares: 10, avgPrice: 140.5, currentPrice: 145.2 },
        { symbol: "GOOG", shares: 5, avgPrice: 2800.0, currentPrice: 2843.5 },
        { symbol: "TSLA", shares: 8, avgPrice: 700.0, currentPrice: 714.6 },
    ];

    const layout = [
        { i: "summary", x: 0, y: 0, w: 12, h: 4 }, // Summary: full width
        { i: "positions", x: 0, y: 4, w: 12, h: 8 }, // Positions table: full width
    ];

    return (
        <GridLayout
            className="layout"
            layout={layout}
            cols={12}
            rowHeight={30}
            width={1200}
            isResizable
            isDraggable
            draggableHandle=".drag-handle"
        >
            {/* Portfolio Summary Tile */}
            <div key="summary">
                <Paper style={{ padding: "16px", height: "100%" }}>
                    <Typography variant="h6" className="drag-handle" style={{ marginBottom: "16px", cursor: "move" }}>
                        Portfolio Summary
                    </Typography>
                    <p>Total Portfolio Value: $32,400</p>
                    <p>Today's Gain/Loss: +$180 (+0.56%)</p>
                </Paper>
            </div>

            {/* Open Positions Tile */}
            <div key="positions">
                <Paper style={{ padding: "16px", height: "100%" }}>
                    <Typography variant="h6" className="drag-handle" style={{ marginBottom: "16px", cursor: "move" }}>
                        Open Positions
                    </Typography>
                    <TableContainer>
                        <Table>
                            <TableHead>
                                <TableRow>
                                    <TableCell><strong>Symbol</strong></TableCell>
                                    <TableCell align="right"><strong>Shares</strong></TableCell>
                                    <TableCell align="right"><strong>Avg Price</strong></TableCell>
                                    <TableCell align="right"><strong>Current Price</strong></TableCell>
                                    <TableCell align="right"><strong>Value</strong></TableCell>
                                </TableRow>
                            </TableHead>
                            <TableBody>
                                {positions.map((position) => (
                                    <TableRow key={position.symbol}>
                                        <TableCell>{position.symbol}</TableCell>
                                        <TableCell align="right">{position.shares}</TableCell>
                                        <TableCell align="right">${position.avgPrice.toFixed(2)}</TableCell>
                                        <TableCell align="right">${position.currentPrice.toFixed(2)}</TableCell>
                                        <TableCell align="right">${(position.shares * position.currentPrice).toFixed(2)}</TableCell>
                                    </TableRow>
                                ))}
                            </TableBody>
                        </Table>
                    </TableContainer>
                </Paper>
            </div>
        </GridLayout>
    );
};

export default Portfolio;
