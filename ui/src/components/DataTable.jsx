import React, { useState } from "react";
import { DataGrid } from "@mui/x-data-grid";
import { TextField } from "@mui/material";

const DataTable = ({ data = [] }) => {  // Ensure data is never undefined
    const [search, setSearch] = useState("");

    const columns = [
        { field: "symbol", headerName: "Symbol", width: 120 },
        { field: "price", headerName: "Price", width: 120 },
        { field: "change", headerName: "Change", width: 100 },
        { field: "volume", headerName: "Volume", width: 120 },
    ];

    // Ensure filteredData is always an array before calling .filter
    const filteredData = Array.isArray(data) ?
        data.filter((row) => row.symbol?.toLowerCase().includes(search.toLowerCase()))
        : [];

    return (
        <div style={{ height: 300, width: "100%" }}>
            <TextField
                label="Search Symbol"
                variant="outlined"
                fullWidth
                style={{ marginBottom: "10px" }}
                onChange={(e) => setSearch(e.target.value)}
            />
            <DataGrid
                rows={filteredData}
                columns={columns}
                pageSize={5}
                getRowId={(row) => row.symbol} // Ensure unique ID for each row
            />
        </div>
    );
};

export default DataTable;
