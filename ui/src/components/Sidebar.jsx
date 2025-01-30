import React, { useState } from "react";
import { Drawer, List, ListItem, ListItemIcon, ListItemText, IconButton } from "@mui/material";
import DashboardIcon from "@mui/icons-material/Dashboard";
import ShowChartIcon from "@mui/icons-material/ShowChart";
import AccountBalanceWalletIcon from "@mui/icons-material/AccountBalanceWallet";
import MenuIcon from "@mui/icons-material/Menu";
import { useNavigate } from "react-router-dom";

const Sidebar = () => {
    const [open, setOpen] = useState(true);
    const navigate = useNavigate();

    const toggleDrawer = () => setOpen(!open);

    return (
        <Drawer variant="permanent" open={open} sx={{ width: open ? 240 : 60, flexShrink: 0 }}>
            <IconButton onClick={toggleDrawer} sx={{ margin: 1 }}>
                <MenuIcon />
            </IconButton>
            <List>
                <ListItem button onClick={() => navigate("/")}>
                    <ListItemIcon><DashboardIcon /></ListItemIcon>
                    {open && <ListItemText primary="Dashboard" />}
                </ListItem>
                <ListItem button onClick={() => navigate("/charting")}>
                    <ListItemIcon><ShowChartIcon /></ListItemIcon>
                    {open && <ListItemText primary="Charting" />}
                </ListItem>
                <ListItem button onClick={() => navigate("/portfolio")}>
                    <ListItemIcon><AccountBalanceWalletIcon /></ListItemIcon>
                    {open && <ListItemText primary="Portfolio" />}
                </ListItem>
            </List>
        </Drawer>
    );
};

export default Sidebar;
