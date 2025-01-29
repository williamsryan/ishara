import React, { useEffect, useState } from "react";
import axios from "axios";
import { Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper } from "@mui/material";

const Watchlist = () => {
    const [watchlist, setWatchlist] = useState([]);

    useEffect(() => {
        const fetchWatchlistData = async () => {
            try {
                const response = await axios.get("/api/stocks/watchlist");
                setWatchlist(response.data);
            } catch (error) {
                console.error("Error fetching watchlist data:", error);
            }
        };

        fetchWatchlistData();
    }, []);

    return (
        <TableContainer component={Paper}>
            <Table>
                <TableHead>
                    <TableRow>
                        <TableCell>Symbol</TableCell>
                        <TableCell>Price</TableCell>
                        <TableCell>Change</TableCell>
                    </TableRow>
                </TableHead>
                <TableBody>
                    {watchlist.length > 0 ? (
                        watchlist.map((stock) => (
                            <TableRow key={stock.symbol}>
                                <TableCell>{stock.symbol}</TableCell>
                                <TableCell>${stock.price.toFixed(2)}</TableCell>
                                <TableCell style={{ color: stock.change >= 0 ? "green" : "red" }}>
                                    {stock.change.toFixed(2)}%
                                </TableCell>
                            </TableRow>
                        ))
                    ) : (
                        <TableRow>
                            <TableCell colSpan={3} style={{ textAlign: "center" }}>No Data Available</TableCell>
                        </TableRow>
                    )}
                </TableBody>
            </Table>
        </TableContainer>
    );
};

export default Watchlist;
