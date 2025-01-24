import React from "react";
import { Layout, Typography } from "antd";

const { Header: AntHeader } = Layout;
const { Title } = Typography;

const Header = () => {
    return (
        <AntHeader style={{ background: "#001529", padding: "0 16px" }}>
            <Title level={3} style={{ color: "#fff", margin: 0 }}>
                📊 Ishara Trading Dashboard
            </Title>
        </AntHeader>
    );
};

export default Header;
