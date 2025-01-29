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
export const fetchChartData = async () => {
    const response = await api.get(`/charts`);
    return response.data;
};

// Fetch stock ticker autocomplete suggestions
export const searchStockSymbols = async (query) => {
    const response = await fetch(`/stocks/search?query=${query}`);
    if (!response.ok) {
        return [];
    }
    return await response.json();
};

// Fetch historical stock data
export const fetchHistoricalData = async (symbol, startDate, endDate) => {
    const query = new URLSearchParams({
        symbols: symbol,
        start_date: startDate,
        end_date: endDate,
    });

    const response = await fetch(`/api/charts/historical/?${query.toString()}`);
    if (!response.ok) {
        throw new Error("Failed to fetch historical data");
    }

    return response.json();
};

export default api;
