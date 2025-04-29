import React, { useEffect, useState } from "react";
import { Stage, Layer, Line, Text } from "react-konva";

const PriceChart = ({ symbol }) => {
    const [data, setData] = useState([]);
    const [width, setWidth] = useState(600);
    const [height, setHeight] = useState(300);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const response = await fetch(`https://api.example.com/stock/${symbol}`);
                const json = await response.json();
                setData(json.prices); // Assume it returns an array of price points
            } catch (error) {
                console.error("Error fetching stock data:", error);
            }
        };

        fetchData();
    }, [symbol]);

    // Convert stock data into points for the chart
    const chartPoints = data.map((point, index) => ({
        x: (index / data.length) * width,
        y: height - (point.price / Math.max(...data.map((p) => p.price))) * height,
    }));

    return (
        <Stage width={width} height={height}>
            <Layer>
                <Text text={symbol} fontSize={18} x={10} y={10} fill="black" />
                <Line points={chartPoints.flatMap((p) => [p.x, p.y])} stroke="blue" strokeWidth={2} />
            </Layer>
        </Stage>
    );
};

export default PriceChart;
