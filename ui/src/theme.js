import { createTheme } from "@mui/material/styles";

const theme = createTheme({
    palette: {
        mode: "light",
        primary: {
            main: "#3b82f6",
        },
        secondary: {
            main: "#f50057",
        },
        background: {
            default: "#f7f8fa",
            paper: "#ffffff",
        },
        text: {
            primary: "#333",
            secondary: "#555",
        },
    },
});

export default theme;
