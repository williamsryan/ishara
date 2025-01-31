import React from "react";
import { Box, Typography } from "@mui/material";

const Footer = () => {
    return (
        <Box
            className="footer-container"
            sx={{
                position: "fixed",
                bottom: 0,
                left: 0,
                width: "100%",
                height: "40px",
                background: "#fff",
                borderTop: "1px solid #ddd",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                fontSize: "14px",
                color: "#555",
                zIndex: 1000,
            }}
        >
            <Typography variant="body2">© 2025 Assertion Labs. All rights reserved.</Typography>
        </Box>
    );
};

export default Footer;
