import React, { useState } from "react";
import { AppBar, Toolbar, Typography, InputBase, Button } from "@mui/material";
import { styled, alpha } from "@mui/material/styles";

const Search = styled("div")(({ theme }) => ({
    position: "relative",
    borderRadius: theme.shape.borderRadius,
    backgroundColor: alpha(theme.palette.common.white, 0.15),
    "&:hover": { backgroundColor: alpha(theme.palette.common.white, 0.25) },
    marginLeft: 0,
    width: "auto",
    display: "flex",
    alignItems: "center",
    padding: "5px 10px",
}));

const Header = ({ onSearch }) => {
    const [ticker, setTicker] = useState("");
    const [startDate, setStartDate] = useState("");
    const [endDate, setEndDate] = useState("");

    const handleSearch = () => {
        onSearch(ticker, startDate, endDate);
    };

    return (
        <AppBar position="static">
            <Toolbar>
                <Typography variant="h6" sx={{ flexGrow: 1 }}>
                    Ishara Dashboard
                </Typography>
                <Search>
                    <InputBase
                        placeholder="Search Ticker"
                        onChange={(e) => setTicker(e.target.value)}
                        value={ticker}
                    />
                    <InputBase
                        type="date"
                        onChange={(e) => setStartDate(e.target.value)}
                        value={startDate}
                    />
                    <InputBase
                        type="date"
                        onChange={(e) => setEndDate(e.target.value)}
                        value={endDate}
                    />
                    <Button onClick={handleSearch} variant="contained">Get Data</Button>
                </Search>
            </Toolbar>
        </AppBar>
    );
};

export default Header;
