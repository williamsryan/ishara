import React, { useState } from "react";
import { Grid, Paper, Typography, TextField, Button, Switch, FormControlLabel, ToggleButtonGroup, ToggleButton } from "@mui/material";

const SettingsPage = () => {
    const [theme, setTheme] = useState("system");

    const handleThemeChange = (_, newTheme) => {
        if (newTheme !== null) {
            setTheme(newTheme);
            // Implement actual theme switching logic here
        }
    };

    return (
        <Grid container spacing={2} sx={{ padding: "16px" }}>
            {/* Account Settings */}
            <Grid item xs={12}>
                <Paper sx={{ padding: "16px" }}>
                    <Typography variant="h6">Account Settings</Typography>
                    <TextField label="Username" fullWidth margin="normal" defaultValue="User123" />
                    <TextField label="Email" type="email" fullWidth margin="normal" defaultValue="user@example.com" />
                    <Button variant="contained" color="primary" sx={{ marginTop: "16px" }}>
                        Save Changes
                    </Button>
                </Paper>
            </Grid>

            {/* Notification Preferences */}
            <Grid item xs={12}>
                <Paper sx={{ padding: "16px" }}>
                    <Typography variant="h6">Notification Preferences</Typography>
                    <FormControlLabel control={<Switch />} label="Email Notifications" />
                    <FormControlLabel control={<Switch />} label="SMS Notifications" />
                </Paper>
            </Grid>

            {/* Theme Toggle */}
            <Grid item xs={12}>
                <Paper sx={{ padding: "16px" }}>
                    <Typography variant="h6">Theme Settings</Typography>
                    <Typography variant="body1">Select Theme Mode</Typography>
                    <ToggleButtonGroup
                        value={theme}
                        exclusive
                        onChange={handleThemeChange}
                        sx={{ marginTop: "10px" }}
                    >
                        <ToggleButton value="light">Light</ToggleButton>
                        <ToggleButton value="dark">Dark</ToggleButton>
                        <ToggleButton value="system">System</ToggleButton>
                    </ToggleButtonGroup>
                </Paper>
            </Grid>
        </Grid>
    );
};

export default SettingsPage;
