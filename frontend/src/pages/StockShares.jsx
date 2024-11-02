import React, {useCallback, useEffect, useRef, useState} from 'react';
import "../styles/stock.css"
import {useFetching} from "../hooks/useFetching";
import StockServices from "../API/StockServices";
import AdaptiveLoading from "../components/UI/AdaptiveLoading";
import BlankResult from "../components/UI/BlankResult/BlankResult";
import {useAuth} from "../hooks/context/useAuth";
import {Link} from "react-router-dom";
import {useObserver} from "../hooks/useObserver";
import BuySharesWholesale from "../components/UI/Forms/BuySharesWholesale";
import {decodeSharesType} from "../functions/utils";

const StockShares = () => {
    const {isAuth} = useAuth();
    const [page, setPage] = useState(1);
    const [hasNext, setNext] = useState(false);
    const lastElement = useRef();
    const [shares, setShares] = useState([]);
    const [fetchShares, isSharesLoading, error] = useFetching(useCallback(async () => {
        const data = await StockServices.getStockShares(page);
        setShares((prevShares) => {
            const newShares = data.data.filter(
                (share) => !prevShares.some((obj) => obj.id === share.id)
            )
            return [...prevShares, ...newShares]
        })
        setNext(data.has_next)
    }, [page]))

    useObserver(lastElement, fetchShares, isSharesLoading, hasNext, page, setPage);

    useEffect(() => {
        const loadData = async () => {
            await fetchShares();
        }
        void loadData();
    }, [page])

    if(isSharesLoading === true || isSharesLoading === null) {
        return <div className={"global__loading"}><AdaptiveLoading/></div>
    }

    return (
        <div className={"section__main"}>
            <div className={"field__shares"}>
                {shares.length > 0 ? (
                    <div className={"shares__list"}>
                        {shares.map((share, index) => (
                            <div className={"share__item"} key={share.ticker} ref={index === shares.length - 1 ? lastElement : null}>
                                <Link to={`/companies/${share.ticker}/`} className={"share__title"}>{share.name}</Link>
                                <div className={"share__row"}>
                                    <div>ticker</div>
                                    <div>{share.ticker}</div>
                                </div>
                                <div className={"share__row"}>
                                    <div>amount</div>
                                    <div>{share.total_amount}</div>
                                </div>
                                <div className={"share__row"}>
                                    <div>minimal price</div>
                                    <div>{share.price}</div>
                                </div>
                                <div className={"share__row"}>
                                    <div>type</div>
                                    <div>{decodeSharesType(share.shares_type)}</div>
                                </div>
                            {isAuth ? (
                                <BuySharesWholesale ticker={share.ticker} sharesType={share.shares_type}/>
                            ) : (
                                <div className={"lon_in_wish_container"}>
                                    <div className={"log_in_wish"}>Sign In!</div>
                                </div>
                            )}
                            </div>
                        ))}
                    </div>
                ) : !error ? (
                    <BlankResult title={"server problem"} info={"Data hasn't been initialized yet"}/>
                ) : (
                    <BlankResult title={"Server Error"} info={"No reply from the server"}/>
                )}
            </div>
        </div>
    );
};

export default StockShares;