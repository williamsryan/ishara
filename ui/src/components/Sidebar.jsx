import React from "react";
import { Drawer, List, ListItem, ListItemIcon, ListItemText, IconButton, Toolbar } from "@mui/material";
import { Home, BarChart, AccountBalanceWallet, Settings, Menu } from "@mui/icons-material";
import { Link } from "react-router-dom";
import { styled } from "@mui/material/styles";

const drawerWidth = 250;
const collapsedWidth = 60;

const Main = styled("main", { shouldForwardProp: (prop) => prop !== "open" })(({ open }) => ({
    marginLeft: open ? drawerWidth : collapsedWidth,
    transition: "margin 0.3s ease-in-out",
    padding: "20px",
}));

const Sidebar = ({ open, handleToggle }) => {
    return (
        <Drawer
            variant="permanent"
            sx={{
                width: open ? drawerWidth : collapsedWidth,
                flexShrink: 0,
                "& .MuiDrawer-paper": {
                    width: open ? drawerWidth : collapsedWidth,
                    transition: "width 0.3s ease-in-out",
                    backgroundColor: "#181a1f", // Darker background for better contrast
                    color: "#d1d1d1", // Lighter gray text for better readability
                    borderRight: "1px solid #333",
                },
            }}
        >
            <Toolbar>
                <IconButton onClick={handleToggle} sx={{ color: "#d1d1d1", margin: "10px" }}>
                    <Menu />
                </IconButton>
            </Toolbar>
            <List>
                <ListItem
                    button
                    component={Link}
                    to="/"
                    sx={{
                        color: "#d1d1d1", // Default lighter text
                        "&:hover": { backgroundColor: "#292b33", color: "#ffffff" },
                        "&.Mui-selected": { backgroundColor: "#3a3f4b", color: "#ffffff" },
                        transition: "background 0.2s ease-in-out",
                        borderRadius: "6px",
                    }}
                >
                    <ListItemIcon sx={{ color: "#d1d1d1" }}>
                        <Home />
                    </ListItemIcon>
                    {open && <ListItemText primary="Dashboard" sx={{ fontWeight: "bold" }} />}
                </ListItem>

                <ListItem
                    button
                    component={Link}
                    to="/charting"
                    sx={{
                        color: "#d1d1d1",
                        "&:hover": { backgroundColor: "#292b33", color: "#ffffff" },
                        "&.Mui-selected": { backgroundColor: "#3a3f4b", color: "#ffffff" },
                        transition: "background 0.2s ease-in-out",
                        borderRadius: "6px",
                    }}
                >
                    <ListItemIcon sx={{ color: "#d1d1d1" }}>
                        <BarChart />
                    </ListItemIcon>
                    {open && <ListItemText primary="Charting" sx={{ fontWeight: "bold" }} />}
                </ListItem>

                <ListItem
                    button
                    component={Link}
                    to="/portfolio"
                    sx={{
                        color: "#d1d1d1",
                        "&:hover": { backgroundColor: "#292b33", color: "#ffffff" },
                        "&.Mui-selected": { backgroundColor: "#3a3f4b", color: "#ffffff" },
                        transition: "background 0.2s ease-in-out",
                        borderRadius: "6px",
                    }}
                >
                    <ListItemIcon sx={{ color: "#d1d1d1" }}>
                        <AccountBalanceWallet />
                    </ListItemIcon>
                    {open && <ListItemText primary="Portfolio" sx={{ fontWeight: "bold" }} />}
                </ListItem>

                <ListItem
                    button
                    component={Link}
                    to="/settings"
                    sx={{
                        color: "#d1d1d1",
                        "&:hover": { backgroundColor: "#292b33", color: "#ffffff" },
                        "&.Mui-selected": { backgroundColor: "#3a3f4b", color: "#ffffff" },
                        transition: "background 0.2s ease-in-out",
                        borderRadius: "6px",
                    }}
                >
                    <ListItemIcon sx={{ color: "#d1d1d1" }}>
                        <Settings />
                    </ListItemIcon>
                    {open && <ListItemText primary="Settings" sx={{ fontWeight: "bold" }} />}
                </ListItem>
            </List>
        </Drawer>
    );
};

export default Sidebar;
