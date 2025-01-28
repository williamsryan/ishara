import React, { useEffect, useState } from "react";
import { fetchStockData } from "../utils/api";

const Stocks = () => {
    const [stocks, setStocks] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const getStocks = async () => {
            try {
                const data = await fetchStockData();
                setStocks(data);
                setLoading(false);
            } catch (err) {
                setError("Failed to load stock data.");
                setLoading(false);
            }
        };
        getStocks();
    }, []);

    if (loading) return <div>Loading stocks...</div>;
    if (error) return <div>{error}</div>;

    return (
        <div>
            <h1>Stocks</h1>
            <table>
                <thead>
                    <tr>
                        <th>Symbol</th>
                        <th>Price</th>
                        <th>Volume</th>
                    </tr>
                </thead>
                <tbody>
                    {stocks.map((stock) => (
                        <tr key={stock.symbol}>
                            <td>{stock.symbol}</td>
                            <td>{stock.price}</td>
                            <td>{stock.volume}</td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
};

export default Stocks;
