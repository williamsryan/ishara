import React, { useState, useEffect } from "react";
import { Box, Typography, IconButton, Tooltip } from "@mui/material";
import { Replay, Wifi, WifiOff } from "@mui/icons-material";

const Footer = ({ refreshData }) => {
    const [currentTime, setCurrentTime] = useState(new Date());
    const [connectionQuality, setConnectionQuality] = useState("good"); // Default: good

    // Update time every second
    useEffect(() => {
        const timer = setInterval(() => {
            setCurrentTime(new Date());
        }, 1000);
        return () => clearInterval(timer);
    }, []);

    // Simulate connection quality updates (replace with actual logic)
    useEffect(() => {
        const qualityCheck = setInterval(() => {
            const qualities = ["good", "moderate", "poor", "offline"];
            setConnectionQuality(qualities[Math.floor(Math.random() * qualities.length)]);
        }, 5000);
        return () => clearInterval(qualityCheck);
    }, []);

    // Format time and date to EST format
    const formatTime = (date) => {
        return date.toLocaleTimeString("en-US", { timeZone: "America/New_York", hour12: false });
    };

    const formatDate = (date) => {
        return date.toLocaleDateString("en-US", { timeZone: "America/New_York", weekday: "short", month: "short", day: "numeric", year: "numeric" });
    };

    // Determine connection icon based on quality
    const getConnectionIcon = () => {
        switch (connectionQuality) {
            case "good":
                return <Wifi sx={{ color: "green" }} />;
            case "moderate":
                return <Wifi sx={{ color: "orange" }} />;
            case "poor":
                return <Wifi sx={{ color: "red" }} />;
            case "offline":
            default:
                return <WifiOff sx={{ color: "gray" }} />;
        }
    };

    return (
        <Box
            className="footer-container"
            sx={{
                position: "fixed",
                bottom: 0,
                right: 0,
                width: "100%",
                height: "30px",
                background: "#121212",
                borderTop: "1px solid #333",
                display: "flex",
                alignItems: "center",
                justifyContent: "flex-end",
                fontSize: "14px",
                color: "#bbb",
                padding: "0 15px",
                zIndex: 1000,
            }}
        >
            {/* Refresh Button */}
            <Tooltip title="Refresh Charts & Panels">
                <IconButton onClick={refreshData} sx={{ color: "#bbb", padding: "4px" }}>
                    <Replay fontSize="small" />
                </IconButton>
            </Tooltip>

            {/* Current Date */}
            <Typography variant="body2" sx={{ marginLeft: "10px", fontSize: "12px" }}>
                {formatDate(currentTime)}
            </Typography>

            {/* Real-Time EST Clock */}
            <Typography variant="body2" sx={{ marginLeft: "10px", fontSize: "12px" }}>
                {formatTime(currentTime)} EST
            </Typography>

            {/* Connection Status Icon */}
            <Tooltip title={`Connection: ${connectionQuality.toUpperCase()}`}>
                <Box sx={{ marginLeft: "10px", display: "flex", alignItems: "center" }}>
                    {getConnectionIcon()}
                </Box>
            </Tooltip>
        </Box>
    );
};

export default Footer;
