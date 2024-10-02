import Main from "../pages/Main";
import Auth from "../pages/Auth";


export const publicRotes = [
    {path: "/", component: <Main/>, key: "main"},
]

export const unprivateRotes = [
    {path: "/authentication/", component: <Auth/>, key: "login"}
]
