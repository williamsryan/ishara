import React, { useState } from "react";
import { Drawer, List, ListItem, ListItemIcon, ListItemText, IconButton } from "@mui/material";
import { Dashboard, BarChart, ShowChart, Menu } from "@mui/icons-material";

const Sidebar = ({ onCollapse }) => {
    const [collapsed, setCollapsed] = useState(false);

    return (
        <Drawer variant="permanent" className={`sidebar ${collapsed ? 'collapsed' : ''}`}>
            <IconButton onClick={() => {
                setCollapsed(!collapsed);
                onCollapse(!collapsed);
            }}>
                <Menu style={{ color: "white" }} />
            </IconButton>
            <List>
                <ListItem button>
                    <ListItemIcon><Dashboard style={{ color: "white" }} /></ListItemIcon>
                    {!collapsed && <ListItemText primary="Dashboard" />}
                </ListItem>
                <ListItem button>
                    <ListItemIcon><ShowChart style={{ color: "white" }} /></ListItemIcon>
                    {!collapsed && <ListItemText primary="Market" />}
                </ListItem>
                <ListItem button>
                    <ListItemIcon><BarChart style={{ color: "white" }} /></ListItemIcon>
                    {!collapsed && <ListItemText primary="Portfolio" />}
                </ListItem>
            </List>
        </Drawer>
    );
};

export default Sidebar;
