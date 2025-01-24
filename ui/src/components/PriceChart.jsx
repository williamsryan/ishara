import React, { useEffect, useState } from "react";
import Plot from "react-plotly.js";
import { fetchPriceData } from "../utils/api";

const PriceChart = () => {
    const [data, setData] = useState([]);
    const [layout, setLayout] = useState({});

    useEffect(() => {
        fetchPriceData().then((response) => {
            setData(response.data);
            setLayout({
                title: "Stock Prices",
                xaxis: { title: "Date" },
                yaxis: { title: "Price" },
            });
        });
    }, []);

    return <Plot data={data} layout={layout} />;
};

export default PriceChart;
