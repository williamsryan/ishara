import React, { useEffect, useState } from "react";
import { Paper, Typography, Table, TableBody, TableCell, TableContainer, TableHead, TableRow } from "@mui/material";
import { fetchPortfolioData } from "../utils/api";

const Portfolio = () => {
    const [data, setData] = useState({
        stocks: [],
        stock_prices: [],
        options: [],
        trades: [],
        earnings: [],
        key_metrics: [],
        historical_prices: [],
        real_time_prices: [],
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

    return (
        <div>
            <Typography variant="h4">Portfolio Overview</Typography>

            {/* Stock Holdings */}
            <Paper style={{ padding: "16px", marginBottom: "16px" }}>
                <Typography variant="h6">Stock Holdings</Typography>
                <TableContainer>
                    <Table>
                        <TableHead>
                            <TableRow>
                                <TableCell>Symbol</TableCell>
                                <TableCell>Name</TableCell>
                                <TableCell>Sector</TableCell>
                                <TableCell>Market Cap</TableCell>
                            </TableRow>
                        </TableHead>
                        <TableBody>
                            {data.stocks.map((stock) => (
                                <TableRow key={stock.symbol}>
                                    <TableCell>{stock.symbol}</TableCell>
                                    <TableCell>{stock.name}</TableCell>
                                    <TableCell>{stock.sector}</TableCell>
                                    <TableCell>${stock.market_cap?.toFixed(2)}</TableCell>
                                </TableRow>
                            ))}
                        </TableBody>
                    </Table>
                </TableContainer>
            </Paper>

            {/* Stock Prices */}
            <Paper style={{ padding: "16px", marginBottom: "16px" }}>
                <Typography variant="h6">Stock Prices</Typography>
                <TableContainer>
                    <Table>
                        <TableHead>
                            <TableRow>
                                <TableCell>Symbol</TableCell>
                                <TableCell>Open</TableCell>
                                <TableCell>High</TableCell>
                                <TableCell>Low</TableCell>
                                <TableCell>Close</TableCell>
                                <TableCell>Volume</TableCell>
                            </TableRow>
                        </TableHead>
                        <TableBody>
                            {data.stock_prices.map((price) => (
                                <TableRow key={price.id}>
                                    <TableCell>{price.symbol}</TableCell>
                                    <TableCell>${price.open?.toFixed(2)}</TableCell>
                                    <TableCell>${price.high?.toFixed(2)}</TableCell>
                                    <TableCell>${price.low?.toFixed(2)}</TableCell>
                                    <TableCell>${price.close?.toFixed(2)}</TableCell>
                                    <TableCell>{price.volume}</TableCell>
                                </TableRow>
                            ))}
                        </TableBody>
                    </Table>
                </TableContainer>
            </Paper>

            {/* Options Data */}
            <Paper style={{ padding: "16px", marginBottom: "16px" }}>
                <Typography variant="h6">Options Holdings</Typography>
                <TableContainer>
                    <Table>
                        <TableHead>
                            <TableRow>
                                <TableCell>Symbol</TableCell>
                                <TableCell>Strike Price</TableCell>
                                <TableCell>Expiration Date</TableCell>
                                <TableCell>Type</TableCell>
                                <TableCell>Last Price</TableCell>
                            </TableRow>
                        </TableHead>
                        <TableBody>
                            {data.options.map((option) => (
                                <TableRow key={option.id}>
                                    <TableCell>{option.symbol}</TableCell>
                                    <TableCell>${option.strike_price.toFixed(2)}</TableCell>
                                    <TableCell>{new Date(option.expiration_date).toLocaleDateString()}</TableCell>
                                    <TableCell>{option.option_type}</TableCell>
                                    <TableCell>${option.last_price.toFixed(2)}</TableCell>
                                </TableRow>
                            ))}
                        </TableBody>
                    </Table>
                </TableContainer>
            </Paper>

            {/* Trades Data */}
            <Paper style={{ padding: "16px", marginBottom: "16px" }}>
                <Typography variant="h6">Trade History</Typography>
                <TableContainer>
                    <Table>
                        <TableHead>
                            <TableRow>
                                <TableCell>Symbol</TableCell>
                                <TableCell>Price</TableCell>
                                <TableCell>Size</TableCell>
                                <TableCell>Timestamp</TableCell>
                            </TableRow>
                        </TableHead>
                        <TableBody>
                            {data.trades.map((trade) => (
                                <TableRow key={trade.id}>
                                    <TableCell>{trade.symbol}</TableCell>
                                    <TableCell>${trade.price.toFixed(2)}</TableCell>
                                    <TableCell>{trade.size}</TableCell>
                                    <TableCell>{new Date(trade.timestamp).toLocaleString()}</TableCell>
                                </TableRow>
                            ))}
                        </TableBody>
                    </Table>
                </TableContainer>
            </Paper>

            {/* Repeat similar sections for `earnings`, `key_metrics`, `historical_prices`, and `real_time_prices` */}
        </div>
    );
};

export default Portfolio;
