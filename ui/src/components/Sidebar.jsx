import React from "react";
import { List, ListItem, ListItemIcon, ListItemText, Divider } from "@mui/material";
import { Home, ShowChart, AccountBalanceWallet, Settings } from "@mui/icons-material";
import { Link } from "react-router-dom";

const Sidebar = () => {
    const menuItems = [
        { name: "Dashboard", icon: <Home />, route: "/" },
        { name: "Charting", icon: <ShowChart />, route: "/charting" },
        { name: "Portfolio", icon: <AccountBalanceWallet />, route: "/portfolio" },
        { name: "Settings", icon: <Settings />, route: "/settings" },
    ];

    return (
        <div
            style={{
                width: "250px",
                backgroundColor: "#f0f2f5",
                padding: "16px",
                height: "100vh",
            }}
        >
            <List>
                {menuItems.map((item, index) => (
                    <React.Fragment key={item.name}>
                        <ListItem button component={Link} to={item.route} style={{ padding: "10px 16px" }}>
                            <ListItemIcon style={{ minWidth: "36px" }}>{item.icon}</ListItemIcon>
                            <ListItemText primary={item.name} />
                        </ListItem>
                        {index < menuItems.length - 1 && <Divider />}
                    </React.Fragment>
                ))}
            </List>
        </div>
    );
};

export default Sidebar;
