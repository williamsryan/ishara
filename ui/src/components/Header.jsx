import React from "react";
import { AppBar, Toolbar, Typography, IconButton } from "@mui/material";
import { Menu } from "@mui/icons-material";

const Header = ({ sidebarOpen, toggleSidebar }) => {
    return (
        <AppBar
            position="fixed"
            sx={{
                backgroundColor: "#1c1e26",
                color: "white",
                transition: "width 0.3s ease-in-out",
                width: sidebarOpen ? "calc(100% - 250px)" : "calc(100% - 60px)",
                marginLeft: sidebarOpen ? "250px" : "60px",
                zIndex: 1300, // Ensure it stays above other elements
            }}
        >
            <Toolbar>
                {/* <IconButton color="inherit" onClick={toggleSidebar} edge="start" sx={{ marginRight: 2 }}>
                    <Menu />
                </IconButton> */}
                <Typography variant="h6" noWrap>
                    Ishara Dashboard
                </Typography>
            </Toolbar>
        </AppBar>
    );
};

export default Header;
