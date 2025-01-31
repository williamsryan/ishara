import React from "react";
import { Box, IconButton } from "@mui/material";
import { ChevronLeft, ChevronRight } from "@mui/icons-material";
import { Link } from "react-router-dom";
import DashboardIcon from "@mui/icons-material/Dashboard";
import ShowChartIcon from "@mui/icons-material/ShowChart";
import AccountBalanceWalletIcon from "@mui/icons-material/AccountBalanceWallet";
import SettingsIcon from "@mui/icons-material/Settings";

const drawerWidth = 200; // Reduce sidebar width
const collapsedWidth = 60;

const Sidebar = ({ open, handleToggle }) => {
    return (
        <Box
            sx={{
                width: open ? drawerWidth : collapsedWidth,
                transition: "width 0.3s ease-in-out",
                height: "100vh",
                background: "#121212",
                color: "#fff",
                display: "flex",
                flexDirection: "column",
                position: "relative",
                paddingTop: "10px",
            }}
        >
            {/* Sidebar Icons & Links */}
            <Box sx={{ display: "flex", flexDirection: "column", alignItems: "flex-start", width: "100%", marginTop: "20px", paddingLeft: "12px" }}>
                <Link to="/" style={{ textDecoration: "none", color: "inherit", display: "flex", alignItems: "center", gap: "8px", padding: "8px" }}>
                    <DashboardIcon sx={{ fontSize: 20 }} />
                    {open && <span style={{ fontSize: "14px" }}>Dashboard</span>}
                </Link>
                <Link to="/charting" style={{ textDecoration: "none", color: "inherit", display: "flex", alignItems: "center", gap: "8px", padding: "8px" }}>
                    <ShowChartIcon sx={{ fontSize: 20 }} />
                    {open && <span style={{ fontSize: "14px" }}>Charting</span>}
                </Link>
                <Link to="/portfolio" style={{ textDecoration: "none", color: "inherit", display: "flex", alignItems: "center", gap: "8px", padding: "8px" }}>
                    <AccountBalanceWalletIcon sx={{ fontSize: 20 }} />
                    {open && <span style={{ fontSize: "14px" }}>Portfolio</span>}
                </Link>
                <Link to="/settings" style={{ textDecoration: "none", color: "inherit", display: "flex", alignItems: "center", gap: "8px", padding: "8px" }}>
                    <SettingsIcon sx={{ fontSize: 20 }} />
                    {open && <span style={{ fontSize: "14px" }}>Settings</span>}
                </Link>
            </Box>

            {/* Webull-Style Toggle Arrow Button */}
            <IconButton
                className="sidebar-toggle"
                onClick={handleToggle}
                sx={{
                    position: "absolute",
                    top: "50%",
                    right: "-12px",
                    transform: "translateY(-50%)",
                    background: "#fff",
                    borderRadius: "6px",
                    padding: "6px",
                    border: "1px solid #ddd",
                    width: "25px",
                    height: "50px",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    cursor: "pointer",
                    zIndex: 1000,
                    "&:hover": { background: "#f0f0f0" },
                }}
            >
                {open ? <ChevronLeft sx={{ color: "#000" }} /> : <ChevronRight sx={{ color: "#000" }} />}
            </IconButton>
        </Box>
    );
};

export default Sidebar;
