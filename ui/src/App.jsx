import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Stocks from "./pages/Stocks";
import Options from "./pages/Options";
import Sidebar from "./components/Sidebar";
import Dashboard from "./pages/Dashboard";
import ChartingPage from "./pages/ChartingPage";
import Portfolio from "./pages/Portfolio";
import SettingsPage from "./pages/SettingsPage";

const App = () => {
  return (
    <Router>
      <div style={{ display: "flex" }}>
        <Sidebar />
        <div style={{ flex: 1 }}>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/stocks" element={<Stocks />} />
            <Route path="/options" element={<Options />} />
            <Route path="/charting" element={<ChartingPage />} />
            <Route path="/portfolio" element={<Portfolio />} />
            <Route path="/settings" element={<SettingsPage />} />
          </Routes>
        </div>
      </div>
    </Router>
  );
};

export default App;
