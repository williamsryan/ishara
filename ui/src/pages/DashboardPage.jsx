import React, { useState } from "react";
import { Box, Grid, Paper, Typography, Tabs, Tab, Table, TableBody, TableCell, TableContainer, TableHead, TableRow } from "@mui/material";
import PriceChart from "../components/PriceChart";
import Watchlist from "../components/Watchlist";
import DataTable from "../components/DataTable";
import PortfolioOverview from "../components/PortfolioOverview";
import OrderPanel from "../components/OrderPanel";
import "../styles/dashboardpage.css";

const DashboardPage = () => {
    const [selectedTab, setSelectedTab] = useState(0);

    return (
        <Box className="dashboard-container">
            <Grid container spacing={1}>

                {/* Left Sidebar */}
                <Grid item xs={2.5}>
                    <Paper className="dashboard-widget sidebar-container">
                        <Typography variant="h6">Top Options</Typography>
                        <Watchlist />
                    </Paper>
                    <Paper className="dashboard-widget sidebar-container">
                        <Typography variant="h6">Market Data</Typography>
                        <DataTable />
                    </Paper>
                </Grid>

                {/* Center Panel */}
                <Grid item xs={7}>
                    <Paper className="dashboard-widget chart-container">
                        <Typography variant="h6">Stock Price Chart</Typography>
                        <PriceChart symbol="SPY" />
                    </Paper>
                    <Paper className="dashboard-widget options-table">
                        <Tabs value={selectedTab} onChange={(_, newValue) => setSelectedTab(newValue)}>
                            <Tab label="Options Chain" />
                            <Tab label="Time & Sales" />
                        </Tabs>
                        {selectedTab === 0 ? <OptionsTable /> : <TimeSales />}
                    </Paper>
                </Grid>

                {/* Right Sidebar */}
                <Grid item xs={2.5}>
                    <Paper className="dashboard-widget sidebar-container">
                        <Typography variant="h6">Quote</Typography>
                        <Typography variant="body1">NVDA $130 31 Jan 25 (W) Call 100</Typography>
                        <Typography variant="body2">0.01 -96.55%</Typography>
                    </Paper>
                    <Paper className="dashboard-widget sidebar-container">
                        <Typography variant="h6">Key Statistics</Typography>
                        <TableContainer>
                            <Table size="small">
                                <TableBody>
                                    <TableRow><TableCell>Open</TableCell><TableCell>0.20</TableCell></TableRow>
                                    <TableRow><TableCell>High</TableCell><TableCell>0.27</TableCell></TableRow>
                                    <TableRow><TableCell>Low</TableCell><TableCell>0.01</TableCell></TableRow>
                                    <TableRow><TableCell>Impl Vol</TableCell><TableCell>3.77%</TableCell></TableRow>
                                </TableBody>
                            </Table>
                        </TableContainer>
                    </Paper>
                    <Paper className="dashboard-widget sidebar-container">
                        <Typography variant="h6">Order Book (BBO)</Typography>
                        <Typography variant="body2">Please login to view details.</Typography>
                    </Paper>
                </Grid>

            </Grid>
        </Box>
    );
};

/* Placeholder Options Table */
const OptionsTable = () => (
    <TableContainer>
        <Table size="small">
            <TableHead>
                <TableRow>
                    <TableCell>Strike</TableCell>
                    <TableCell>Bid</TableCell>
                    <TableCell>Ask</TableCell>
                    <TableCell>IV</TableCell>
                </TableRow>
            </TableHead>
            <TableBody>
                <TableRow><TableCell>117</TableCell><TableCell>0.30</TableCell><TableCell>0.45</TableCell><TableCell>29.5%</TableCell></TableRow>
                <TableRow><TableCell>120</TableCell><TableCell>0.15</TableCell><TableCell>0.20</TableCell><TableCell>31.2%</TableCell></TableRow>
            </TableBody>
        </Table>
    </TableContainer>
);

/* Placeholder Time & Sales */
const TimeSales = () => (
    <TableContainer>
        <Table size="small">
            <TableHead>
                <TableRow>
                    <TableCell>Time</TableCell>
                    <TableCell>Price</TableCell>
                    <TableCell>Size</TableCell>
                </TableRow>
            </TableHead>
            <TableBody>
                <TableRow><TableCell>15:59:32</TableCell><TableCell>0.01</TableCell><TableCell>100</TableCell></TableRow>
                <TableRow><TableCell>15:58:20</TableCell><TableCell>0.02</TableCell><TableCell>50</TableCell></TableRow>
            </TableBody>
        </Table>
    </TableContainer>
);

export default DashboardPage;
