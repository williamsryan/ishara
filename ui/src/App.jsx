import React from "react";
import { Layout } from "antd";
import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
import Header from "./components/Header";
import Sidebar from "./components/Sidebar";
import Dashboard from "./pages/Dashboard";
import BacktestingPage from "./pages/BacktestingPage";

const { Content } = Layout;

const App = () => {
  return (
    <Router>
      <Layout style={{ minHeight: "100vh" }}>
        {/* Sidebar Navigation */}
        <Sidebar />
        <Layout>
          {/* Header */}
          <Header />
          {/* Content Area */}
          <Content style={{ margin: "24px", background: "#fff", padding: "16px" }}>
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/backtesting" element={<BacktestingPage />} />
            </Routes>
          </Content>
        </Layout>
      </Layout>
    </Router>
  );
};

export default App;
