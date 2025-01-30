import React, { useState } from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import { CssBaseline, Box } from "@mui/material";
import Sidebar from "./components/Sidebar";
import Header from "./components/Header";
import Footer from "./components/Footer";
import DashboardPage from "./pages/DashboardPage";
import ChartingPage from "./pages/ChartingPage";
import PortfolioPage from "./pages/PortfolioPage";
import SettingsPage from "./pages/SettingsPage";

const drawerWidth = 250;
const collapsedWidth = 60;

const App = () => {
  const [sidebarOpen, setSidebarOpen] = useState(true);

  const toggleSidebar = () => {
    setSidebarOpen(!sidebarOpen);
  };

  return (
    <Router>
      <CssBaseline />
      <Box sx={{ display: "flex", flexDirection: "column", minHeight: "100vh" }}>
        <Header sidebarOpen={sidebarOpen} toggleSidebar={toggleSidebar} />
        <Box sx={{ display: "flex", flexGrow: 1, overflow: "hidden", marginTop: "64px" }}>
          <Sidebar open={sidebarOpen} handleToggle={toggleSidebar} />
          <Box
            component="main"
            sx={{
              flexGrow: 1,
              transition: "all 0.3s ease-in-out",
              padding: "20px",
              display: "flex",
              flexDirection: "column",
              width: sidebarOpen ? `calc(100% - ${drawerWidth}px)` : `calc(100% - ${collapsedWidth}px)`,
            }}
          >
            <Routes>
              <Route path="/" element={<DashboardPage />} />
              <Route path="/charting" element={<ChartingPage />} />
              <Route path="/portfolio" element={<PortfolioPage />} />
              <Route path="/settings" element={<SettingsPage />} />
            </Routes>
          </Box>
        </Box>
        <Footer sidebarOpen={sidebarOpen} />
      </Box>
    </Router>
  );
};

export default App;
