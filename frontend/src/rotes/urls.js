import Main from "../pages/Main";
import Auth from "../pages/Auth";
import Laws from "../pages/Laws";
import News from "../pages/News";
import StockGold from "../pages/StockGold";
import Companies from "../pages/Companies";
import StockProducts from "../pages/StockProducts";
import StockShares from "../pages/StockShares";
import Company from "../pages/Company";
//understand why styles are imported all at once

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

]
