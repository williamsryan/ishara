import React, { useEffect, useState } from "react";
import {
    Paper,
    Typography,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    TablePagination,
} from "@mui/material";
import Draggable from "react-draggable";
import { ResizableBox } from "react-resizable";
import { fetchPortfolioData } from "../utils/api";

import "react-resizable/css/styles.css"; // Required for resizable components

const Portfolio = () => {
    const [data, setData] = useState({
        stocks: [],
        stock_prices: [],
        options: [],
        trades: [],
    });
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const getPortfolio = async () => {
            try {
                const result = await fetchPortfolioData();
                setData(result);
                setLoading(false);
            } catch (err) {
                setError("Failed to load portfolio data.");
                setLoading(false);
            }
        };
        getPortfolio();
    }, []);

    if (loading) return <div>Loading portfolio...</div>;
    if (error) return <div>{error}</div>;

    // Resizable Table Component
    const ResizableTable = ({ title, rows, columns }) => (
        <Draggable handle=".drag-handle">
            <ResizableBox width={800} height={400} minConstraints={[400, 300]} maxConstraints={[1200, 800]}>
                <Paper style={{ padding: "16px", marginBottom: "16px", height: "100%", overflow: "auto" }}>
                    <Typography
                        variant="h6"
                        className="drag-handle"
                        style={{ marginBottom: "16px", cursor: "move" }}
                    >
                        {title}
                    </Typography>
                    <TableContainer>
                        <Table>
                            <TableHead>
                                <TableRow>
                                    {columns.map((col) => (
                                        <TableCell key={col}>{col}</TableCell>
                                    ))}
                                </TableRow>
                            </TableHead>
                            <TableBody>
                                {rows.map((row, index) => (
                                    <TableRow key={index}>
                                        {Object.values(row).map((cell, idx) => (
                                            <TableCell key={idx}>{cell}</TableCell>
                                        ))}
                                    </TableRow>
                                ))}
                            </TableBody>
                        </Table>
                    </TableContainer>
                </Paper>
            </ResizableBox>
        </Draggable>
    );

    return (
        <div>
            <Typography variant="h4" style={{ marginBottom: "16px" }}>
                Portfolio Overview
            </Typography>

            {/* Stock Holdings */}
            <ResizableTable
                title="Stock Holdings"
                rows={data.stocks.map((stock) => ({
                    Symbol: stock.symbol,
                    Name: stock.name,
                    Sector: stock.sector,
                    MarketCap: `$${stock.market_cap?.toFixed(2)}`,
                }))}
                columns={["Symbol", "Name", "Sector", "Market Cap"]}
            />

            {/* Stock Prices */}
            <ResizableTable
                title="Stock Prices"
                rows={data.stock_prices.map((price) => ({
                    Symbol: price.symbol,
                    Open: `$${price.open?.toFixed(2)}`,
                    High: `$${price.high?.toFixed(2)}`,
                    Low: `$${price.low?.toFixed(2)}`,
                    Close: `$${price.close?.toFixed(2)}`,
                    Volume: price.volume,
                }))}
                columns={["Symbol", "Open", "High", "Low", "Close", "Volume"]}
            />

            {/* Options Holdings */}
            <ResizableTable
                title="Options Holdings"
                rows={data.options.map((option) => ({
                    Symbol: option.symbol,
                    StrikePrice: `$${option.strike_price.toFixed(2)}`,
                    Expiration: new Date(option.expiration_date).toLocaleDateString(),
                    Type: option.option_type,
                    LastPrice: `$${option.last_price.toFixed(2)}`,
                }))}
                columns={["Symbol", "Strike Price", "Expiration", "Type", "Last Price"]}
            />

            {/* Trade History */}
            <ResizableTable
                title="Trade History"
                rows={data.trades.map((trade) => ({
                    Symbol: trade.symbol,
                    Price: `$${trade.price.toFixed(2)}`,
                    Size: trade.size,
                    Timestamp: new Date(trade.timestamp).toLocaleString(),
                }))}
                columns={["Symbol", "Price", "Size", "Timestamp"]}
            />
        </div>
    );
};

export default Portfolio;
