import React, { useState } from "react";
import { TextField, Button } from "@mui/material";
import SearchIcon from "@mui/icons-material/Search";

const Header = ({ onSearch }) => {
    const [search, setSearch] = useState("");

    return (
        <header className="header">
            <h1>Ishara Dashboard</h1>
            <div className="search-container">
                <TextField
                    variant="outlined"
                    size="small"
                    placeholder="Search Ticker"
                    value={search}
                    onChange={(e) => setSearch(e.target.value)}
                />
                <Button variant="contained" onClick={() => onSearch(search)}>
                    <SearchIcon />
                </Button>
            </div>
        </header>
    );
};

export default Header;
