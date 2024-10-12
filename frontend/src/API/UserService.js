import apiClient from "../hooks/useApiInterceptor";

export default class UserService {
    static async getUserInfo() {
        const response = await apiClient.get(`/user/`)
        return response.data
    }
    static async getUserCompanies(page, limit, fields) {
        const response = await apiClient.get(`/user/companies/`, {params: {page: page,
                ...(limit ? { limit } : {}), ...(fields ? {fields} : {})}})
        return response.data
    }
    static async getUserShares(page) {
        const response = await apiClient.get(`/user/shares/`, {params: {page: page}})
        return response.data
    }
    static async megreCompanies(companyType, selectedCompanies, ticker, name, shares_amount, preferredSharesAmount, dividendesPercent) {
        const response = await apiClient.post(`//user/companies/`,  {type: companyType,
            companies: selectedCompanies, ticker, name, shares_amount, preferred_shares_amount: preferredSharesAmount,
            dividendes: dividendesPercent}
        )
        return response.data
    }
}