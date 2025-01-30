import React from "react";
import { Box, Typography } from "@mui/material";

const drawerWidth = 250;
const collapsedWidth = 60;

const Footer = ({ sidebarOpen }) => {
    return (
        <Box
            sx={{
                backgroundColor: "#1E1E1E",
                color: "white",
                padding: "10px",
                textAlign: "center",
                width: `calc(100% - ${sidebarOpen ? drawerWidth : collapsedWidth}px)`,
                marginLeft: sidebarOpen ? `${drawerWidth}px` : `${collapsedWidth}px`,
                transition: "width 0.3s ease-in-out, margin 0.3s ease-in-out",
            }}
        >
            <Typography variant="body2">© 2025 Assertion Labs. All rights reserved.</Typography>
        </Box>
    );
};

export default Footer;
