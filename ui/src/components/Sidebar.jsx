import React from "react";
import { Layout, Menu } from "antd";
import {
    LineChartOutlined,
    BarChartOutlined,
    TableOutlined,
    ExperimentOutlined,
} from "@ant-design/icons";
import { Link } from "react-router-dom";

const { Sider } = Layout;

const Sidebar = () => {
    return (
        <Sider collapsible>
            <Menu theme="dark" mode="inline" defaultSelectedKeys={["1"]}>
                <Menu.Item key="1" icon={<LineChartOutlined />}>
                    <Link to="/">Live Market</Link>
                </Menu.Item>
                <Menu.Item key="2" icon={<BarChartOutlined />}>
                    <Link to="/backtesting">Backtesting</Link>
                </Menu.Item>
                <Menu.Item key="3" icon={<TableOutlined />}>
                    <Link to="/data-table">Data Table</Link>
                </Menu.Item>
                <Menu.Item key="4" icon={<ExperimentOutlined />}>
                    <Link to="/analyses">Analyses</Link>
                </Menu.Item>
            </Menu>
        </Sider>
    );
};

export default Sidebar;
