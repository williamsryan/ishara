import React from "react";
import "../styles/orderbook.css";

const OrderBook = () => {
    return (
        <div className="order-book">
            <h3>Orders</h3>
            <table>
                <thead>
                    <tr>
                        <th>Symbol</th>
                        <th>Type</th>
                        <th>Quantity</th>
                        <th>Price</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>AAPL</td>
                        <td>Limit Buy</td>
                        <td>10</td>
                        <td>$235.50</td>
                        <td>Pending</td>
                    </tr>
                    <tr>
                        <td>TSLA</td>
                        <td>Market Sell</td>
                        <td>5</td>
                        <td>$672.10</td>
                        <td>Executed</td>
                    </tr>
                </tbody>
            </table>
        </div>
    );
};

export default OrderBook;
