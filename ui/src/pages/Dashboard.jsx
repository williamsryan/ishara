import React from "react";
import PriceChart from "../components/PriceChart";
import OrderPanel from "../components/OrderPanel";

const Dashboard = () => {
    return (
        <div style={{ display: "flex", padding: "16px" }}>
            <div style={{ flex: 3 }}>
                <PriceChart />
            </div>
            <div style={{ flex: 1, marginLeft: "16px" }}>
                <OrderPanel />
            </div>
        </div>
    );
};

export default Dashboard;
