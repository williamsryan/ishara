import React from "react";
import { AppBar, Toolbar, Typography, Box } from "@mui/material";

const Header = ({ sidebarOpen }) => {
    return (
        <AppBar
            position="fixed"
            sx={{
                width: "100%", // Remove left margin to prevent empty space
                background: "#121212",
                color: "#fff",
                boxShadow: "none",
            }}
        >
            <Toolbar>
                <Typography variant="h6" noWrap component="div">
                    Ishara Dashboard
                </Typography>
            </Toolbar>
        </AppBar>
    );
};

export default Header;
