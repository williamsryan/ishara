import React, { useEffect, useState } from "react";
import { fetchWatchlist, addToWatchlist, removeFromWatchlist } from "../utils/api";
import "../styles/Watchlist.css";

const Watchlist = () => {
    const [watchlist, setWatchlist] = useState([]);
    const [symbol, setSymbol] = useState("");
    const [error, setError] = useState(null);

    const loadWatchlist = async () => {
        try {
            const data = await fetchWatchlist();
            setWatchlist(data);
        } catch (err) {
            setError(err.message);
        }
    };

    const handleAddStock = async () => {
        if (!symbol.trim()) return;
        try {
            await addToWatchlist(symbol);
            setSymbol("");
            loadWatchlist();
        } catch (err) {
            setError(err.message);
        }
    };

    const handleRemoveStock = async (stockSymbol) => {
        try {
            await removeFromWatchlist(stockSymbol);
            loadWatchlist();
        } catch (err) {
            setError(err.message);
        }
    };

    useEffect(() => {
        loadWatchlist();
    }, []);

    return (
        <div className="watchlist-widget">
            {/* <h2 className="watchlist-title">Watchlist</h2> */}
            {error && <p className="error">{error}</p>}
            <div className="watchlist-input">
                <input
                    type="text"
                    value={symbol}
                    onChange={(e) => setSymbol(e.target.value.toUpperCase())}
                    placeholder="Add stock symbol"
                />
                <button onClick={handleAddStock}>Add</button>
            </div>
            <ul className="watchlist-container">
                {watchlist.length === 0 ? <p>No stocks in watchlist.</p> : watchlist.map((stock) => (
                    <li key={stock.symbol} className="watchlist-item">
                        {stock.symbol}
                        <button className="remove-button" onClick={() => handleRemoveStock(stock.symbol)}>X</button>
                    </li>
                ))}
            </ul>
        </div>
    );
};

export default Watchlist;
