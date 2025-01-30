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
    const response = await api.get("/charts");
    return response.data;
};

// Fetch stock ticker autocomplete suggestions
export const searchStockSymbols = async (query) => {
    const response = await api.get(`/stocks/search`, {
        params: { query },
    });
    return response.data;
};

// Fetch historical stock data
export const fetchHistoricalData = async (symbol, startDate, endDate) => {
    const response = await api.get(`/charts/historical`, {
        params: { symbols: symbol, start_date: startDate, end_date: endDate },
    });

    return response.data;
};

export const fetchNews = async () => {
    try {
        const response = await axios.get(`${API_BASE_URL}/news`);
        return response.data;
    } catch (error) {
        console.error("Failed to fetch news:", error);
        return [];
    }
};

export const fetchWatchlist = async () => {
    try {
        const response = await axios.get(`${API_BASE_URL}/watchlist`);
        return response.data;
    } catch (error) {
        console.error("Failed to fetch watchlist:", error);
        return [];
    }
};

export default api;
