import React, { useEffect, useState } from "react";
import { fetchOptions } from "../utils/api";

const Options = () => {
    const [options, setOptions] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const data = await fetchOptions();
                setOptions(data);
                setLoading(false);
            } catch (err) {
                setError("Failed to load options data.");
                setLoading(false);
            }
        };
        fetchData();
    }, []);

    if (loading) return <div>Loading options...</div>;
    if (error) return <div>{error}</div>;

    return (
        <div>
            <h1>Options</h1>
            <table>
                <thead>
                    <tr>
                        <th>Symbol</th>
                        <th>Strike</th>
                        <th>Expiration</th>
                        <th>Type</th>
                        <th>Last Price</th>
                    </tr>
                </thead>
                <tbody>
                    {options.map((option) => (
                        <tr key={`${option.symbol}-${option.strike}-${option.expiration}`}>
                            <td>{option.symbol}</td>
                            <td>{option.strike}</td>
                            <td>{option.expiration}</td>
                            <td>{option.type}</td>
                            <td>{option.last_price}</td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
};

export default Options;
