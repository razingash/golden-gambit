import apiClient from "../hooks/useApiInterceptor";

export default class UserService {
    static async getUserInfo() {
        const response = await apiClient.get(`/user/`)
        return response.data
    }
    static async getUserCompanies(page) {
        const response = await apiClient.get(`/user/companies/`, {params: {page: page}})
        return response.data
    }
    static async getUserShares(page) {
        const response = await apiClient.get(`/user/shares/`, {params: {page: page}})
        return response.data
    }
}