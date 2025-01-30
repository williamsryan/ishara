import React, { useEffect, useState } from "react";
import { Paper, Typography, List, ListItem, ListItemText } from "@mui/material";
import api from "../utils/api";

const Watchlist = () => {
    const [watchlist, setWatchlist] = useState([]);
    const [error, setError] = useState(null);

    useEffect(() => {
        async function fetchWatchlist() {
            try {
                const response = await api.get("/watchlist");
                setWatchlist(response.data);
            } catch (err) {
                console.error("Error fetching watchlist:", err);
                setError("Failed to fetch watchlist data.");
            }
        }
        fetchWatchlist();
    }, []);

    return (
        <Paper elevation={3} sx={{ padding: 2 }}>
            <Typography variant="h6">Watchlist</Typography>
            {error ? (
                <Typography color="error">{error}</Typography>
            ) : (
                <List>
                    {watchlist.length > 0 ? (
                        watchlist.map((item, index) => (
                            <ListItem key={index}>
                                <ListItemText primary={`${item.symbol}: ${item.price}`} />
                            </ListItem>
                        ))
                    ) : (
                        <Typography>No watchlist data available</Typography>
                    )}
                </List>
            )}
        </Paper>
    );
};

export default Watchlist;
