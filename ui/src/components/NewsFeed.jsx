import React, { useEffect, useState } from "react";
import { Paper, Typography, List, ListItem, ListItemText } from "@mui/material";
import api from "../utils/api";

const NewsFeed = () => {
    const [news, setNews] = useState([]);
    const [error, setError] = useState(null);

    useEffect(() => {
        async function fetchNews() {
            try {
                const response = await api.get("/news");
                setNews(response.data);
            } catch (err) {
                console.error("Error fetching news:", err);
                setError("Failed to fetch market news.");
            }
        }
        fetchNews();
    }, []);

    return (
        <Paper elevation={3} sx={{ padding: 2 }}>
            <Typography variant="h6">Market News</Typography>
            {error ? (
                <Typography color="error">{error}</Typography>
            ) : (
                <List>
                    {news.length > 0 ? (
                        news.map((item, index) => (
                            <ListItem key={index}>
                                <ListItemText primary={item.headline} secondary={item.source} />
                            </ListItem>
                        ))
                    ) : (
                        <Typography>No news available</Typography>
                    )}
                </List>
            )}
        </Paper>
    );
};

export default NewsFeed;
