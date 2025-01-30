import React, { useState } from "react";
import { Link } from "react-router-dom";
import DashboardIcon from "@mui/icons-material/Dashboard";
import ShowChartIcon from "@mui/icons-material/ShowChart";
import AccountBalanceWalletIcon from "@mui/icons-material/AccountBalanceWallet";
import TuneIcon from "@mui/icons-material/Tune";
import MenuIcon from "@mui/icons-material/Menu";

const Sidebar = () => {
    const [collapsed, setCollapsed] = useState(false);

    return (
        <aside className={`sidebar ${collapsed ? "collapsed" : ""}`}>
            <button className="menu-button" onClick={() => setCollapsed(!collapsed)}>
                <MenuIcon />
            </button>
            <nav>
                <ul>
                    <li>
                        <Link to="/"><DashboardIcon /> Dashboard</Link>
                    </li>
                    <li>
                        <Link to="/charting"><ShowChartIcon /> Charting</Link>
                    </li>
                    <li>
                        <Link to="/portfolio"><AccountBalanceWalletIcon /> Portfolio</Link>
                    </li>
                    <li>
                        <Link to="/screener"><TuneIcon /> Screener</Link>
                    </li>
                </ul>
            </nav>
        </aside>
    );
};

export default Sidebar;
