import {lazy} from "react";

const Main = lazy(() => import("../pages/Main"));
const Auth = lazy(() => import("../pages/Auth"));
const Laws = lazy(() => import("../pages/Laws"));
const News = lazy(() => import("../pages/News"));
const StockGold = lazy(() => import("../pages/StockGold"));
const Companies = lazy(() => import("../pages/Companies"));
const StockProducts = lazy(() => import("../pages/StockProducts"));
const StockShares = lazy(() => import("../pages/StockShares"));
const Company = lazy(() => import("../pages/Company"));
const Profile = lazy(() => import("../pages/Profile/Profile"));
const UserCompanies = lazy(() => import("../pages/Profile/UserCompanies"));
const UserShares = lazy(() => import("../pages/Profile/UserShares"));
const UserCompaniesRecipes = lazy(() => import("../pages/Profile/UserCompaniesRecipes"));


export const publicRotes = [
    {path: "/", component: <Main/>, key: "main"},
    {path: "/laws/", component: <Laws/>, key: "laws"},
    {path: "/news/", component: <News/>, key: "news"},
    {path: "/stock/", component: <StockGold/>, key: "stock-gold"},
    {path: "/stock/products/", component: <StockProducts/>, key: "stock-products"},
    {path: "/stock/shares/", component: <StockShares/>, key: "stock-shares"},
    {path: "/companies/", component: <Companies/>, key: "companies"},
    {path: "/companies/:ticker/", component: <Company/>, key: "companies"}
]

export const unprivateRotes = [
    {path: "/authentication/", component: <Auth/>, key: "login"}
]

export const privateRotes = [
    {path: "/profile/", component: <Profile/>, key: "profile", children: [
        {path: "/profile/tickers/", component: <UserCompanies/>, key: "user-tickers"},
        {path: "/profile/recipes", component: <UserCompaniesRecipes/>, key: "user-tickers-recipies"},
        {path: "/profile/shares/", component: <UserShares/>, key: "user-shares"},
        ]
    },
]
