import React from "react";
import { DataGrid } from "@mui/x-data-grid";

const columns = [
    { field: "symbol", headerName: "Symbol", width: 100 },
    { field: "price", headerName: "Price", width: 100 },
    { field: "change", headerName: "Change", width: 100 },
    { field: "volume", headerName: "Volume", width: 150 },
];

const MarketDataTable = ({ data }) => {
    return (
        <div className="data-table">
            <DataGrid rows={data} columns={columns} pageSize={5} />
        </div>
    );
};

export default MarketDataTable;
