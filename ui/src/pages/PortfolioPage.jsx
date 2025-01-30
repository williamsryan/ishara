import React, { useEffect, useState } from "react";
import PortfolioTable from "../components/PortfolioTable";
import axios from "axios";

const PortfolioPage = () => {
    const [portfolio, setPortfolio] = useState([]);

    useEffect(() => {
        axios.get("/api/portfolio").then((res) => setPortfolio(res.data));
    }, []);

    return (
        <div className="portfolio-page">
            <h2>My Portfolio</h2>
            <PortfolioTable data={portfolio} />
        </div>
    );
};

export default PortfolioPage;
