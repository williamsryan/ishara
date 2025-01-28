import axios from "axios";

const BASE_URL = "http://localhost:1337/api";

// Axios instance
const api = axios.create({
    baseURL: BASE_URL,
    timeout: 10000, // 10 seconds timeout
});

// Fetch stock data
export const fetchStockData = async () => {
    const response = await api.get("/stocks");
    return response.data;
};

// Fetch options data
export const fetchOptions = async () => {
    const response = await api.get("/options");
    return response.data;
};

// Fetch portfolio data
export const fetchPortfolioData = async () => {
    const response = await api.get("/portfolio");
    return response.data;
};

// Fetch chart data
export const fetchChartData = async (symbol) => {
    const response = await api.get(`/charts/${symbol}`);
    return response.data;
};

export default api;
