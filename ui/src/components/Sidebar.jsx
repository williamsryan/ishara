import React from "react";
import { Link } from "react-router-dom";

const Sidebar = () => {
    return (
        <div style={{ width: "200px", backgroundColor: "#f0f2f5", height: "100vh" }}>
            <ul>
                <li><Link to="/">Dashboard</Link></li>
                <li><Link to="/backtesting">Backtesting</Link></li>
            </ul>
        </div>
    );
};

export default Sidebar;
