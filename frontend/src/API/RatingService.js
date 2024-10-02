import axios from "axios";
import {baseURL} from "../hooks/useApiInterceptor";

export default class RatingService {
    static async getTopCompanies() {
        const response = await axios.get(`${baseURL}/top/companies/`)
        return response.data
    }
    static async getTopUsers() {
        const response = await axios.get(`${baseURL}/top/users/`)
        return response.data
    }
}