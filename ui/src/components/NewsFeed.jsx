import React, { useEffect, useState } from "react";
import axios from "axios";
import { List, ListItem, ListItemText, Paper, Typography } from "@mui/material";

const NewsFeed = () => {
    const [news, setNews] = useState([]);

    useEffect(() => {
        const fetchNewsData = async () => {
            try {
                const response = await axios.get("/api/news");
                setNews(response.data);
            } catch (error) {
                console.error("Error fetching news:", error);
            }
        };

        fetchNewsData();
    }, []);

    return (
        <Paper style={{ padding: "15px", maxHeight: "300px", overflowY: "auto" }}>
            <Typography variant="h6" gutterBottom>
                {/* Market News */}
            </Typography>
            <List>
                {news.length > 0 ? (
                    news.map((article, index) => (
                        <ListItem key={index} component="a" href={article.url} target="_blank" rel="noopener noreferrer">
                            <ListItemText
                                primary={article.headline}
                                secondary={`${article.source} | ${new Date(article.timestamp).toLocaleString()}`}
                            />
                        </ListItem>
                    ))
                ) : (
                    <Typography variant="body2" style={{ textAlign: "center" }}>
                        No news available
                    </Typography>
                )}
            </List>
        </Paper>
    );
};

export default NewsFeed;
