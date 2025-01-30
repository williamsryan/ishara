import React, { useEffect, useState } from "react";
import axios from "axios";
import { DataGrid } from "@mui/x-data-grid";

const columns = [
    { field: "symbol", headerName: "Symbol", width: 100 },
    { field: "company", headerName: "Company", width: 200 },
    { field: "date", headerName: "Earnings Date", width: 150 },
    { field: "eps", headerName: "EPS Estimate", width: 100 },
];

const EarningsCalendar = () => {
    const [earnings, setEarnings] = useState([]);

    useEffect(() => {
        axios.get("/api/earnings").then((res) => setEarnings(res.data));
    }, []);

    return (
        <div className="earnings-calendar">
            <h3>Upcoming Earnings</h3>
            <DataGrid rows={earnings} columns={columns} pageSize={5} />
        </div>
    );
};

export default EarningsCalendar;
