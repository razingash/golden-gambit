import axios from "axios";
import {baseURL} from "../hooks/useApiInterceptor";

export default class LawsService {
    static async getLawsList() {
        const response = await axios.get(`${baseURL}/laws/`)
        return response.data
    }
}