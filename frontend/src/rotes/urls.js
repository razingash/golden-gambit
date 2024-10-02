import Main from "../pages/Main";
import Auth from "../pages/Auth";
import Laws from "../pages/Laws";
import News from "../pages/News";
import Stock from "../pages/Stock";
import Companies from "../pages/Companies";


export const publicRotes = [
    {path: "/", component: <Main/>, key: "main"},
    {path: "/laws/", component: <Laws/>, key: "laws"},
    {path: "/news/", component: <News/>, key: "news"},
    {path: "/stock/", component: <Stock/>, key: "stock"},
    {path: "/companies/", component: <Companies/>, key: "companies"}
]

export const unprivateRotes = [
    {path: "/authentication/", component: <Auth/>, key: "login"}
]

export const privateRotes = [
    //{path: "/companies/:ticker/", component: <Companies/>, key: "companies"}
]
