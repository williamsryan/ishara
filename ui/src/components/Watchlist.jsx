import React, { useState, useEffect } from "react";
import { Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper, Typography } from "@mui/material";
import axios from "axios";

const Watchlist = () => {
    const [watchlistData, setWatchlistData] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        fetchWatchlistData();
        const interval = setInterval(fetchWatchlistData, 5000); // Refresh data every 5 seconds

        return () => clearInterval(interval);
    }, []);

    const fetchWatchlistData = async () => {
        try {
            const response = await axios.get("/api/stocks"); // Replace with your API endpoint
            setWatchlistData(response.data);
            setLoading(false);
        } catch (err) {
            setError("Failed to fetch watchlist data.");
            setLoading(false);
        }
    };

    return (
        <Paper sx={{ padding: 2, marginTop: 2 }}>
            <Typography variant="h6" sx={{ marginBottom: 2 }}>
                Watchlist
            </Typography>
            {loading ? (
                <Typography>Loading...</Typography>
            ) : error ? (
                <Typography color="error">{error}</Typography>
            ) : (
                <TableContainer component={Paper}>
                    <Table size="small">
                        <TableHead>
                            <TableRow>
                                <TableCell><b>Symbol</b></TableCell>
                                <TableCell><b>Price</b></TableCell>
                                <TableCell><b>Change</b></TableCell>
                                <TableCell><b>Volume</b></TableCell>
                            </TableRow>
                        </TableHead>
                        <TableBody>
                            {watchlistData.length > 0 ? (
                                watchlistData.map((stock, index) => (
                                    <TableRow key={index}>
                                        <TableCell>{stock.symbol}</TableCell>
                                        <TableCell>${stock.price?.toFixed(2) || "N/A"}</TableCell>
                                        <TableCell style={{ color: stock.change >= 0 ? "green" : "red" }}>
                                            {stock.change?.toFixed(2) || "N/A"}%
                                        </TableCell>
                                        <TableCell>{stock.volume?.toLocaleString() || "N/A"}</TableCell>
                                    </TableRow>
                                ))
                            ) : (
                                <TableRow>
                                    <TableCell colSpan={4} align="center">
                                        No Data Available
                                    </TableCell>
                                </TableRow>
                            )}
                        </TableBody>
                    </Table>
                </TableContainer>
            )}
        </Paper>
    );
};

export default Watchlist;
