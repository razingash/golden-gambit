import {createContext, useContext, useEffect, useRef, useState} from "react";
import {useFetching} from "../useFetching";
import AuthService from "../../API/AuthService";

export const AuthContext = createContext(null);

export const useAuth = () => {
    return useContext(AuthContext);
}

export const AuthProvider = ({ children }) => {
    const [isAuth, setIsAuth] = useState(false);
    const tokenRef = useRef({access: null});

    const [fetchRegisteredUser, isRegisteredUserLoading] = useFetching(async (username, password) => {
        return await AuthService.register(username, password)
    })
    const [fetchLoginUser, isUserLoading] = useFetching(async (username, password) => {
        return await AuthService.login(username, password);
    })
    const [fetchLogoutUser] = useFetching(async (refreshToken) => {
        return await AuthService.logout(refreshToken);
    })
    const [fetchVerifiedToken] = useFetching(async (token) => {
        return await AuthService.verifyToken(token);
    })
    const [fetchRefreshedToken, , TokenError] = useFetching(async (refreshToken) => {
        return await AuthService.refreshAccessToken(refreshToken)
    })

    const login = async (username, password) => { // good
        const data = await fetchLoginUser(username, password);
        console.log(data);
        if (isUserLoading === false) {
            localStorage.setItem('token', data.refresh);
            tokenRef.current.access = data.access;
            setIsAuth(true);
        } else {
            console.log("error during login")
            return "bad request?"
        }
    }

    const register = async (username, password) => {
        const data = await fetchRegisteredUser(username, password);
        console.log(data);
        if (isRegisteredUserLoading === false) {
            localStorage.setItem('token', data.refresh)
            tokenRef.current.access = data.access;
            setIsAuth(true);
        } else {
            console.log("error during register")
            return "bad request register?"
        }
    }

    const logout = async () => { // good
        const refreshToken = localStorage.getItem('token');
        if (!refreshToken) { //
            setIsAuth(false);
        }
        else if (refreshToken) {
             await fetchLogoutUser(refreshToken);
        }
        localStorage.removeItem('token')
        tokenRef.current.access = null;
        setIsAuth(false);
    }

    const validateRefreshToken = async () => { // good
        const refreshToken = localStorage.getItem('token')
        if (refreshToken) {
            await fetchVerifiedToken(refreshToken);
            return TokenError !== true; //if false, then refresh token has expired
        } else {
            setIsAuth(false);
            await logout(); // there will be no request bcs refreshToken undefinded
        }
    }

    const refreshAccessToken = async () => { // must be good?
        const isRefreshTokenValid = await validateRefreshToken();
        const refreshToken = localStorage.getItem('token');
        if (isRefreshTokenValid === true) {
            const data = fetchRefreshedToken(refreshToken);
            tokenRef.current.access = data.access;
            setIsAuth(true);
            return data.access
        } else { // refresh token has expired
            localStorage.removeItem('token')
            tokenRef.current.access = null;
            setIsAuth(false);
        }
    }

    useEffect(() => {
        const initializeAuth = async () => { // rave?
            const isRefreshTokenValid = await validateRefreshToken();
            if (isRefreshTokenValid) {
                await refreshAccessToken();
            }
        }
        void initializeAuth();
    }, [isAuth]);

    return (
        <AuthContext.Provider value={{isAuth, tokenRef, register, login, logout, refreshAccessToken, validateRefreshToken}}>
            {children}
        </AuthContext.Provider>
    )
}
