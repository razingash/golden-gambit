import axios from "axios";
import {useEffect} from "react";
import {useAuth} from "./context/useAuth";

//later change
export const websocketBaseURL = 'ws://localhost:8000/ws'
export const baseURL = 'http://127.0.0.1:8000/api/v1' //`${window.location.origin}/api/v1`;

const apiClient = axios.create ({
    baseURL: baseURL,
    headers: {
        'Content-Type': 'application/json',
    }
})

export const useApiInterceptors = () => {
    const { tokenRef, refreshAccessToken } = useAuth();

    useEffect(() => {
        if (!tokenRef.current) return;
        const interceptorId = apiClient.interceptors.request.use(
            (config) => {
                if (tokenRef.current.access) {
                    config.headers.Authorization = `Bearer ${tokenRef.current.access}`;
                    return config;
                }
            },(error) => Promise.reject(error)
        )

        const responseInterceptorId = apiClient.interceptors.response.use(
            (response) => response,async (error) => {
                const originalRequest = error.config;
                if (error.response.status === 401 && !originalRequest._retry) { // perhaps requests like 204 will raise errors
                    originalRequest._retry = true;
                    const accessToken = await refreshAccessToken();
                    apiClient.defaults.headers.common.Authorization = `Bearer ${accessToken}`;
                    originalRequest.headers.Authorization = `Bearer ${accessToken}`;
                    return apiClient(originalRequest);
                }
                return Promise.reject(error);
            }
        )

        return () => {
            apiClient.interceptors.request.eject(interceptorId);
            apiClient.interceptors.response.eject(responseInterceptorId);
        }
    }, [tokenRef])
}

export default apiClient;
