import axios from "axios";
import apiClient, {baseURL} from "../hooks/useApiInterceptor";

export default class StockServices {
    static async getGoldSilverRate() { // future hook
        const response = await axios.get(`${baseURL}/stock/gold/`)
        return response.data
    }
    static async getGoldRateHistory() {
        const response = await axios.get(`${baseURL}/stock/gold/history/`)
        return response.data
    }
    static async getStockProducts() {
        const response = await axios.get(`${baseURL}/stock/products/`)
        return response.data
    }
    static async getStockShares() { // returns data and has_next
        const response = await axios.get(`${baseURL}/stock/shares-exchange/`)
        return response.data
    }
    static async tradeGold(type, amount) { // type - buy or sell
        const response = await apiClient.post(`/stock/gold/${type}/`, {amount})
        return response.data
    }
    static async tradeProducts(type, company_ticker, amount, product_type) {
        const response = await apiClient.post(`/stock/products/${type}/`, {type, company_ticker, amount, product_type})
        return response.data
    }
    static async tradeShares(ticker, shares_type, amount, price) {
        const response = await apiClient.post(`/stock/shares-exchange/${ticker}/`)
        return response.data
    }
}