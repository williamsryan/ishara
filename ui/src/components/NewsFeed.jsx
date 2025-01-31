import React, { useState, useEffect } from "react";
import { fetchNews } from "../utils/api";
import CircularProgress from "@mui/material/CircularProgress";
import "../styles/newsfeed.css";

const NewsFeed = ({ symbols = [] }) => {
    const [news, setNews] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchMarketNews = async () => {
            setLoading(true);
            try {
                const data = await fetchNews(symbols);
                setNews(data.news || []);
            } catch (err) {
                setError("Failed to load news.");
            }
            setLoading(false);
        };

        fetchMarketNews();
        const interval = setInterval(fetchMarketNews, 10000); // Refresh every 10 sec
        return () => clearInterval(interval);
    }, [symbols]);

    return (
        <div className="news-widget">
            {/* <h2 className="news-title">Market News</h2> */}
            {loading && <CircularProgress />}
            {error && <p className="error">{error}</p>}
            <div className="news-container">
                {news.length === 0 && !loading ? (
                    <p>No news available.</p>
                ) : (
                    news.map((article, index) => (
                        <div key={index} className="news-item">
                            <h3 className="news-headline">{article.headline}</h3>
                            <p className="news-summary">{article.summary}</p>
                            <a className="news-link" href={article.url} target="_blank" rel="noopener noreferrer">
                                Read more
                            </a>
                            <p className="news-source">Source: {article.source}</p>
                            <p className="news-date">{new Date(article.created_at).toLocaleString()}</p>
                        </div>
                    ))
                )}
            </div>
        </div>
    );
};

export default NewsFeed;
