import React, { useState } from "react";
import { Drawer, List, ListItem, ListItemIcon, ListItemText, IconButton } from "@mui/material";
import { Dashboard, ShowChart, AccountBalanceWallet, Settings, Menu } from "@mui/icons-material";
import { Link } from "react-router-dom";

const Sidebar = () => {
    const [open, setOpen] = useState(true);

    return (
        <Drawer variant="permanent" open={open}>
            <IconButton onClick={() => setOpen(!open)} style={{ margin: "10px" }}>
                <Menu />
            </IconButton>
            <List>
                <ListItem button component={Link} to="/">
                    <ListItemIcon><Dashboard /></ListItemIcon>
                    {open && <ListItemText primary="Dashboard" />}
                </ListItem>
                <ListItem button component={Link} to="/charting">
                    <ListItemIcon><ShowChart /></ListItemIcon>
                    {open && <ListItemText primary="Charting" />}
                </ListItem>
                <ListItem button component={Link} to="/portfolio">
                    <ListItemIcon><AccountBalanceWallet /></ListItemIcon>
                    {open && <ListItemText primary="Portfolio" />}
                </ListItem>
                <ListItem button component={Link} to="/settings">
                    <ListItemIcon><Settings /></ListItemIcon>
                    {open && <ListItemText primary="Settings" />}
                </ListItem>
            </List>
        </Drawer>
    );
};

export default Sidebar;
