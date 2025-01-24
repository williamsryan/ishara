import React from "react";
import { Tabs } from "antd";
import PriceChart from "../components/PriceChart";
import AlternativeData from "../components/AlternativeData";

const { TabPane } = Tabs;

const Dashboard = () => {
    return (
        <Tabs defaultActiveKey="1">
            <TabPane tab="📈 Price Chart" key="1">
                <PriceChart />
            </TabPane>
            <TabPane tab="📊 Alternative Data" key="2">
                <AlternativeData />
            </TabPane>
        </Tabs>
    );
};

export default Dashboard;
