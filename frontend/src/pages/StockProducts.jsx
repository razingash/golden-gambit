import React, {useEffect, useRef, useState} from 'react';
import "../styles/stock.css"
import {useFetching} from "../hooks/useFetching";
import StockServices from "../API/StockServices";
import BlankResult from "../components/UI/BlankResult/BlankResult";
import AdaptiveLoading from "../components/UI/AdaptiveLoading";
import {useAuth} from "../hooks/context/useAuth";
import {useObserver} from "../hooks/useObserver";
import GlobalTradeProductsForm from "../components/UI/Forms/GlobalTradeProductsForm";
import {decodeProductType} from "../functions/utils";

const StockProducts = () => {
    const {isAuth} = useAuth();
    const [page, setPage] = useState(1);
    const [hasNext, setNext] = useState(false);
    const lastElement = useRef();
    const [products, setProducts] = useState([]);
    const [selectedProductType, setSelectedProductType] = useState(null);
    const [isFormSpawned, setForm] = useState(false);

    const [fetchProducts, isProductsLoading, error] = useFetching(async () => {
        const data = await StockServices.getStockProducts(page);
        setProducts((prevProducts) => {
            const newProducts = data.data.filter(
                (product) => !prevProducts.some((obj) => obj.type === product.type)
            )
            return [...prevProducts, ...newProducts]
        })
        setNext(data.has_next)
    })

    const spawnForm = (productType) => {
        setSelectedProductType(productType);
        setForm(true);
    }
    const closeForm = () => {
        setForm(false);
    }

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
                        <div className={"product__item"} key={product.type} ref={index === products.length - 1 ? lastElement : null}>
                            <div className={"product__info"}>
                                <div className={"product__name"}>{decodeProductType(product.type)}</div>
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
                                <button className={"button__submit stock_products_container_fix"} onClick={() => spawnForm(product.type)}>trade</button>
                            ) : (
                                <div className={"lon_in_wish_container"}>
                                    <div className={"log_in_wish"}>Sign In!</div>
                                </div>
                            )}
                        </div>
                    ))) : !error ? (
                        <BlankResult title={"server problem"} info={"Data hasn't been initialized yet"}/>
                        ) : (
                        <BlankResult title={"Server Error"} info={"No reply from the server"}/>
                        )
                    }
                </div>
            </div>
            {isFormSpawned && <GlobalTradeProductsForm productType={selectedProductType} onClose={closeForm}/>}
        </div>
    );
};

export default StockProducts;