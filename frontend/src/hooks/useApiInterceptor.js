import axios from "axios";

export const baseURL = 'http://127.0.0.1:8000/api/v1'

const apiClient = axios.create ({
    baseURL: baseURL,
    headers: {
        'Content-Type': 'application/json',
    }
})


export default apiClient;
