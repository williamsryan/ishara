import React from "react";
import { List, ListItem, ListItemText, Divider, Button, Typography } from "@mui/material";

const Sidebar = () => {
    const watchlist = [
        { name: "AAPL", change: "-0.38%" },
        { name: "GOOG", change: "+0.81%" },
        { name: "SPX", change: "+1.20%" },
    ];

    return (
        <div
            style={{
                width: "250px",
                backgroundColor: "#f0f2f5",
                padding: "16px",
                height: "100vh",
            }}
        >
            <Typography variant="h6">My Watchlist</Typography>
            <List>
                {watchlist.map((item, index) => (
                    <React.Fragment key={item.name}>
                        <ListItem>
                            <ListItemText
                                primary={`${item.name}`}
                                secondary={`Change: ${item.change}`}
                            />
                        </ListItem>
                        {index < watchlist.length - 1 && <Divider />}
                    </React.Fragment>
                ))}
            </List>
            <Button variant="contained" fullWidth>
                Add Symbol
            </Button>
        </div>
    );
};

export default Sidebar;
