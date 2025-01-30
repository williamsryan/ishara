import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
import Sidebar from "./components/Sidebar";
import Header from "./components/Header";
import Footer from "./components/Footer";
import DashboardPage from "./pages/DashboardPage";
import ChartingPage from "./pages/ChartingPage";
import PortfolioPage from "./pages/PortfolioPage";
import ScreenerPage from "./pages/ScreenerPage";
import MarketPage from "./pages/MarketPage";
import { useState } from "react";
import "./styles/global.css";

function App() {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

  return (
    <Router>
      <div className={`app-container ${sidebarCollapsed ? "collapsed" : ""}`}>
        <Sidebar collapsed={sidebarCollapsed} setCollapsed={setSidebarCollapsed} />
        <div className="main-content">
          <Header />
          <div className="page-content">
            <Routes>
              <Route path="/" element={<DashboardPage />} />
              <Route path="/charting" element={<ChartingPage />} />
              <Route path="/portfolio" element={<PortfolioPage />} />
              <Route path="/screener" element={<ScreenerPage />} />
              <Route path="/market" element={<MarketPage />} />
            </Routes>
          </div>
          <Footer />
        </div>
      </div>
    </Router>
  );
}

export default App;
