import axios from "axios";

const BASE_URL = "http://localhost:1337/api";

// Axios instance with proper base URL
const api = axios.create({
    baseURL: BASE_URL,
    timeout: 10000, // 10 seconds timeout
});

// Generic GET request with error handling
const getRequest = async (endpoint) => {
    try {
        const response = await api.get(endpoint);
        return response.data;
    } catch (error) {
        console.error(`Failed to fetch ${endpoint}:`, error);
        return [];
    }
};

// **Stock Data**
export const fetchStockData = () => getRequest("/stocks");

// **Options Data**
export const fetchOptionsData = () => getRequest("/options");

// **Portfolio Data**
export const fetchPortfolioData = () => getRequest("/portfolio");

// **Chart Data**
export const fetchChartData = () => getRequest("/charts");

// **Stock Ticker Autocomplete**
export const searchStockSymbols = async (query) => {
    try {
        const response = await api.get(`/stocks/search`, { params: { query } });
        return response.data;
    } catch (error) {
        console.error("Failed to fetch stock symbols:", error);
        return [];
    }
};

// **Historical Stock Data**
export const fetchHistoricalData = async (symbol, startDate, endDate) => {
    try {
        const response = await api.get(`/charts/historical/`, {
            params: { symbols: symbol, start_date: startDate, end_date: endDate },
        });
        return response.data;
    } catch (error) {
        console.error("Failed to fetch historical data:", error);
        throw new Error("Error fetching historical data");
    }
};

// **Market News**
export const fetchNews = () => getRequest("/news");

// **Watchlist Data**
export const fetchWatchlist = () => getRequest("/watchlist");

export const addToWatchlist = async (symbol) => {
    const response = await fetch(`${BASE_URL}/watchlist?symbol=${symbol}`, {
        method: "POST"
    });
    if (!response.ok) throw new Error("Failed to add stock to watchlist");
    return response.json();
};

export const removeFromWatchlist = async (symbol) => {
    const response = await fetch(`${BASE_URL}/watchlist/${symbol}`, {
        method: "DELETE"
    });
    if (!response.ok) throw new Error("Failed to remove stock from watchlist");
    return response.json();
};

// **Market Screener**
export const fetchMarketData = () => getRequest("/market");

// **Earnings Calendar**
export const fetchEarningsCalendar = () => getRequest("/earnings");

// Exporting API instance for general use if needed
export default api;
