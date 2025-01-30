import React, { useEffect, useState } from "react";
import axios from "axios";
import { ResponsiveHeatMap } from "@nivo/heatmap";

const HeatMap = () => {
    const [heatmapData, setHeatmapData] = useState([]);

    useEffect(() => {
        axios.get("/api/heatmap").then((res) => setHeatmapData(res.data));
    }, []);

    return (
        <div className="heatmap">
            <h3>Market Heatmap</h3>
            <ResponsiveHeatMap
                data={heatmapData}
                margin={{ top: 50, right: 60, bottom: 50, left: 60 }}
                colors={{ scheme: "red_yellow_green" }}
                axisTop={null}
                axisRight={null}
                axisBottom={{ tickSize: 5, tickPadding: 5, tickRotation: 0, legend: "Sector", legendPosition: "middle", legendOffset: 36 }}
                axisLeft={{ tickSize: 5, tickPadding: 5, tickRotation: 0, legend: "Stock", legendPosition: "middle", legendOffset: -40 }}
            />
        </div>
    );
};

export default HeatMap;
