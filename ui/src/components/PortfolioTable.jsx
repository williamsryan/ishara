import React from "react";
import { DataGrid } from "@mui/x-data-grid";

const columns = [
    { field: "symbol", headerName: "Symbol", width: 100 },
    { field: "shares", headerName: "Shares", width: 100 },
    { field: "avgPrice", headerName: "Avg Price", width: 100 },
    { field: "marketValue", headerName: "Market Value", width: 150 },
];

const PortfolioTable = ({ data }) => {
    return (
        <div className="data-table">
            <DataGrid rows={data} columns={columns} pageSize={5} />
        </div>
    );
};

export default PortfolioTable;
