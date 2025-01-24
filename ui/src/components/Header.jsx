import React from "react";
import { AppBar, Toolbar, Typography, InputBase, Button } from "@mui/material";
import SearchIcon from "@mui/icons-material/Search";

const Header = () => {
    return (
        <AppBar position="static" style={{ backgroundColor: "#001529" }}>
            <Toolbar style={{ display: "flex", justifyContent: "space-between" }}>
                <Typography variant="h6" style={{ color: "#fff" }}>
                    Ishara: Paper Trading
                </Typography>
                <div style={{ display: "flex", alignItems: "center" }}>
                    <SearchIcon style={{ color: "#fff", marginRight: "8px" }} />
                    <InputBase
                        placeholder="Search…"
                        style={{
                            backgroundColor: "#fff",
                            borderRadius: "4px",
                            padding: "4px 8px",
                            width: "200px",
                        }}
                    />
                </div>
                <Button variant="contained" color="secondary">
                    Login
                </Button>
            </Toolbar>
        </AppBar>
    );
};

export default Header;
