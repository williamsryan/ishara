import React from "react";
import { Grid2, Paper, Typography, TextField, Button, Switch, FormControlLabel } from "@mui/material";

const SettingsPage = () => {
    return (
        <Grid2 container spacing={2} style={{ padding: "16px" }}>
            {/* Account Settings */}
            <Grid2 item xs={12}>
                <Paper style={{ padding: "16px" }}>
                    <Typography variant="h6">Account Settings</Typography>
                    <TextField label="Username" fullWidth margin="normal" defaultValue="User123" />
                    <TextField label="Email" type="email" fullWidth margin="normal" defaultValue="user@example.com" />
                    <Button variant="contained" color="primary" style={{ marginTop: "16px" }}>
                        Save Changes
                    </Button>
                </Paper>
            </Grid2>

            {/* Notification Preferences */}
            <Grid2 item xs={12}>
                <Paper style={{ padding: "16px" }}>
                    <Typography variant="h6">Notification Preferences</Typography>
                    <FormControlLabel control={<Switch />} label="Email Notifications" />
                    <FormControlLabel control={<Switch />} label="SMS Notifications" />
                </Paper>
            </Grid2>
        </Grid2>
    );
};

export default SettingsPage;
