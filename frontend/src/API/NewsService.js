import axios from "axios";
import {baseURL} from "../hooks/useApiInterceptor";

export default class NewsService {
    static async getNewsList() {
        const response = await axios.get(`${baseURL}/news/`)
        return response.data
    }
}