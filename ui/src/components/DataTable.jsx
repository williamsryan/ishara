import React, { useState } from "react";
import { DataGrid } from "@mui/x-data-grid";
import { TextField } from "@mui/material";

const DataTable = ({ data }) => {
    const [search, setSearch] = useState("");

    const columns = [
        { field: "symbol", headerName: "Symbol", width: 120 },
        { field: "price", headerName: "Price", width: 120 },
        { field: "change", headerName: "Change", width: 120 },
        { field: "volume", headerName: "Volume", width: 120 },
    ];

    const filteredData = data.filter((row) =>
        row.symbol.toLowerCase().includes(search.toLowerCase())
    );

    return (
        <div style={{ height: 300, width: "100%" }}>
            <TextField
                label="Search Symbol"
                variant="outlined"
                fullWidth
                style={{ marginBottom: "10px" }}
                onChange={(e) => setSearch(e.target.value)}
            />
            <DataGrid rows={filteredData} columns={columns} pageSize={5} />
        </div>
    );
};

export default DataTable;
