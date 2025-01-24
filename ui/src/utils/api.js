import axios from "axios";

const BASE_URL = process.env.REACT_APP_API_URL || "http://localhost:5000/api";

export const fetchPriceData = async () => {
    const response = await axios.get(`${BASE_URL}/price-data`);
    return response.data;
};
