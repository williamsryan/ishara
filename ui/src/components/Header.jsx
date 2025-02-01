import React from "react";
import { AppBar, Toolbar, Box, TextField, Button, InputAdornment } from "@mui/material";
import SearchIcon from "@mui/icons-material/Search";

const Header = () => {
    return (
        <AppBar
            position="fixed"
            sx={{
                width: "100%",
                height: "40px",
                background: "#121212",
                color: "#fff",
                boxShadow: "none",
                display: "flex",
                justifyContent: "center",
                alignItems: "center",
                paddingX: "15px",
            }}
        >
            <Toolbar
                sx={{
                    minHeight: "40px",
                    width: "100%",
                    display: "flex",
                    justifyContent: "flex-end",
                    alignItems: "center",
                    gap: "15px",
                }}
            >
                {/* Ticker Search Bar */}
                <TextField
                    variant="outlined"
                    size="small"
                    placeholder="Search symbol/name"
                    sx={{
                        background: "#1e1e1e",
                        borderRadius: "4px",
                        input: { color: "#fff", padding: "6px 10px" },
                        "& fieldset": { border: "none" },
                        width: "220px",
                    }}
                    InputProps={{
                        startAdornment: (
                            <InputAdornment position="start">
                                <SearchIcon sx={{ color: "#bbb", fontSize: 18 }} />
                            </InputAdornment>
                        ),
                    }}
                />

                {/* Login Button */}
                <Button
                    variant="contained"
                    sx={{
                        background: "#2c2c2c",
                        color: "#fff",
                        fontSize: "12px",
                        padding: "5px 14px",
                        textTransform: "none",
                        borderRadius: "6px",
                        "&:hover": { background: "#3a3a3a" },
                    }}
                >
                    Login
                </Button>
            </Toolbar>
        </AppBar>
    );
};

export default Header;
