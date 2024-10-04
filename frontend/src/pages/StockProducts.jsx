import React, {useEffect, useState} from 'react';
import useInput from "../hooks/useInput";
import {useFetching} from "../hooks/useFetching";
import StockServices from "../API/StockServices";
import BlankResult from "../components/UI/BlankResult/BlankResult";
import AdaptiveLoading from "../components/UI/AdaptiveLoading";
import {useAuth} from "../hooks/context/useAuth";

const StockProducts = () => { // REDO!!!
    const {isAuth} = useAuth();
    const amount = useInput('');
    const ticker = useInput('');
    const tradeType = useInput('buy');
    const tradingTypes = { "purchase": "buy", "sale": "sell" }
    const [products, setProducts] = useState([]);
    const [fetchProducts, isProductsLoading] = useFetching(async () => {
        return await StockServices.getStockProducts();
    })

    const tradeProducts = async (e) => { // improve
        e.preventDefault();
        const error = await fetchProducts();
        if (error) { // improve
            console.log('tradeGold error')
        }
    }

    useEffect(() => { // has_next !
        const loadData = async () => {
            const data = await fetchProducts();
            data && setProducts(data.data);
        }
        void loadData();
    }, [isProductsLoading])

    if (products.length === 0) {
        return (<div className={"global__loading"}><AdaptiveLoading/></div>)
    }

    return (
        <div className={"section__main"}>
            <div className={"field__products"}>
                <div className={"products__list"}>
                    {products.length > 0 ? (products.map((product) => (
                        <div className={"product__item"} key={product.product_type_display}>
                            <div className={"product__info"}>
                                <div className={"product__name"}>{product.product_type_display}</div>
                                <div className={"product__row"}>
                                    <div>purchase</div>
                                    <div>{product.purchase_price}</div>
                                </div>
                                <div className={"product__row"}>
                                    <div>sale</div>
                                    <div>{product.sale_price}</div>
                                </div>
                            </div>
                            {isAuth ? (
                                <form onSubmit={tradeProducts} className={"form__product_trading"}>
                                    <input className={"input__stock"} {...amount} type={"text"} placeholder={"amount"}/>
                                    <input className={"input__stock"} {...ticker} type={"text"} placeholder={"ticker"}/>
                                    <select {...tradingTypes}>
                                        {Object.entries(tradingTypes).map(([trade, type]) => (
                                            <option key={trade} value={type}>{trade}</option>
                                        ))}
                                    </select>
                                </form>
                            ) : (
                               <div className={"log_in_wish"}>Sign In!</div>
                            )}
                        </div>
                    ))): (
                        <BlankResult title={"server problem"} info={"Data hasn't been initialized yet"}/>
                    )}
                </div>
            </div>
        </div>
    );
};

export default StockProducts;