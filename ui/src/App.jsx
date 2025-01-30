import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
import Sidebar from "./components/Sidebar";
import Header from "./components/Header";
import Footer from "./components/Footer";
import DashboardPage from "./pages/DashboardPage";
import ChartingPage from "./pages/ChartingPage";
import PortfolioPage from "./pages/PortfolioPage";
import ScreenerPage from "./pages/ScreenerPage";
import MarketPage from "./pages/MarketPage";
import "./styles/global.css";

function App() {
  return (
    <Router>
      <div className="app-container">
        <Sidebar />
        <div className="main-content">
          <Header />
          <Routes>
            <Route path="/" element={<DashboardPage />} />
            <Route path="/charting" element={<ChartingPage />} />
            <Route path="/portfolio" element={<PortfolioPage />} />
            <Route path="/screener" element={<ScreenerPage />} />
            <Route path="/market" element={<MarketPage />} />
          </Routes>
          <Footer />
        </div>
      </div>
    </Router>
  );
}

export default App;
