import React, {useEffect, useRef, useState} from 'react';
import {useFetching} from "../hooks/useFetching";
import StockServices from "../API/StockServices";
import BlankResult from "../components/UI/BlankResult/BlankResult";
import AdaptiveLoading from "../components/UI/AdaptiveLoading";
import {useAuth} from "../hooks/context/useAuth";
import {useObserver} from "../hooks/useObserver";
import TradeProducts from "../components/UI/Forms/TradeProducts";

const StockProducts = () => {
    const {isAuth} = useAuth();
    const [page, setPage] = useState(1);
    const [hasNext, setNext] = useState(false);
    const lastElement = useRef();
    const [products, setProducts] = useState([]);
    const [fetchProducts, isProductsLoading] = useFetching(async () => {
        const data = await StockServices.getStockProducts(page);
        setProducts((prevProducts) => {
            const newProducts = data.data.filter(
                (product) => !prevProducts.some((obj) => obj.name === product.name)
            )
            return [...prevProducts, ...newProducts]
        })
        setNext(data.has_next)
    })

    useObserver(lastElement, fetchProducts, isProductsLoading, hasNext, page, setPage);

    useEffect(() => {
        const loadData = async () => {
            await fetchProducts();
        }
        void loadData();
    }, [page])

    if (isProductsLoading === true || isProductsLoading === null) {
        return (<div className={"global__loading"}><AdaptiveLoading/></div>)
    }

    return (
        <div className={"section__main"}>
            <div className={"field__products"}>
                <div className={"products__list"}>
                    {products.length > 0 ? (products.map((product, index) => (
                        <div className={"product__item"} key={product.name} ref={index === products.length - 1 ? lastElement : null}>
                            <div className={"product__info"}>
                                <div className={"product__name"}>{product.name}</div>
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
                                <TradeProducts productType={product.type}/>
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