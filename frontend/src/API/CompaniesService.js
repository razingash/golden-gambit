import axios from "axios";
import apiClient, {baseURL} from "../hooks/useApiInterceptor";

export default class CompaniesService {
    static async getCompaniesList(page) {
        const response = await axios.get(`${baseURL}/companies/`, {params: {page: page}})
        return response.data
    }
    static async getCompany(ticker, token) {
        const response = await axios.get(`${baseURL}/companies/${ticker}/`,
            {headers: {Authorization: token ? `Bearer ${token}` : ''}})
        return response.data
    }
    static async getCompanyHistory(ticker) {
        const response = await axios.get(`${baseURL}/companies/${ticker}/history/`)
        return response.data
    }
    static async getCompaniesRecipes() {
        const response = await apiClient.get("/companies/recipes/")
        return response.data
    }
    static async getCompanyInventory(ticker) { // only for company head
        const response = await apiClient.get(`/companies/${ticker}/warehouse/`)
        return response.data
    }
    static async getCompanyNewProducts(ticker) { // only for company head
        const response = await apiClient.get(`/companies/${ticker}/warehouse/update/`)
        return response.data
    }
    static async createNewCompany(type, ticker, name, shares_amount, preferred_shares_amount, dividendes_percent) {
        const response = await apiClient.post(`/user/companies/`,
            {type, ticker, name, shares_amount, preferred_shares_amount, dividendes_percent})
        return response.data
    }
    static async printNewCompanyShares(ticker, shares_type, amount, price) {
        const response = await apiClient.post(`/companies/${ticker}/exchange/`, {shares_type, amount, price})
        return response.data
    }
    static async sellUserShares(ticker, shares_type, amount, price) {
        const response = await apiClient.post(`/companies/${ticker}/sell-shares/`, {shares_type, amount, price})
        return response.data
    }
    static async changeUserCompany(ticker, data) { //data should be dict
        const response = await apiClient.patch(`/companies/${ticker}/`, data)
        return response.data
    }
}