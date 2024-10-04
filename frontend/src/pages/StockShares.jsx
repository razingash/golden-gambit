import React, {useEffect, useState} from 'react';
import useInput from "../hooks/useInput";
import {useFetching} from "../hooks/useFetching";
import StockServices from "../API/StockServices";
import AdaptiveLoading from "../components/UI/AdaptiveLoading";
import BlankResult from "../components/UI/BlankResult/BlankResult";
import {useAuth} from "../hooks/context/useAuth";
import {Link} from "react-router-dom";

const StockShares = () => {
    // add smart sorting - There are shares of the same company - then do it like in Steam so that when you select the quantity, the price is automatically calculated
    const {isAuth} = useAuth();
    const amount = useInput('');
    const ticker = useInput('');
    const tradeType = useInput('buy');
    const tradingTypes = { "purchase": "buy", "sale": "sell" }
    const [shares, setShares] = useState([]);
    const [fetchShares, isSharesLoading] = useFetching(async () => {
        return await StockServices.getStockShares();
    })

    useEffect(() => { // has_next !
        const loadData = async () => {
            const data = await fetchShares();
            data && setShares(data.data);
        }
        void loadData();
    }, [isSharesLoading])

    if(shares.length === 0) {
        return (<div className={"global__loading"}><AdaptiveLoading/></div>)
    }

    return (
        <div className={"section__main"}>
            <div className={"field__shares"}>
                {shares.length > 0 ? (
                    <div className={"shares__list"}>
                        {shares.map((share, index) => (
                            <div className={"share__item"} key={index}>
                                <Link to={`/companies/${share.ticker}/`} className={"share__title"}>{share.name}</Link>
                                <div className={"share__row"}>
                                    <div>ticker</div>
                                    <div>{share.ticker}</div>
                                </div>
                                <div className={"share__row"}>
                                    <div>amount</div>
                                    <div>{share.amount}</div>
                                </div>
                                <div className={"share__row"}>
                                    <div>price</div>
                                    <div>{share.price}</div>
                                </div>
                            {isAuth ? (
                                <div>REDO</div>
                            ) : (
                                <div className={"log_in_wish"}>Sign In!</div>
                            )}
                            </div>
                        ))}
                    </div>
                ) : (
                    <BlankResult title={"server problem"} info={"Data hasn't been initialized yet"}/>
                )}
                <div className={"shares__item"}></div>
            </div>
        </div>
    );
};

export default StockShares;