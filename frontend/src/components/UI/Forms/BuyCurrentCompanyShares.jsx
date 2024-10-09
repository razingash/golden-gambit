import React from 'react';
import useInput from "../../../hooks/useInput";
import {useFetching} from "../../../hooks/useFetching";
import StockServices from "../../../API/StockServices";

const BuyCurrentCompanyShares = ({ticker, sharesType, price} ) => {
    const amount = useInput('');
    const tradeType = useInput('buy');

    const [fetchTradeShares, ,shareError] = useFetching(async () => {
        return await StockServices.tradeShares(ticker, sharesType, amount.value, price)
    })

    const tradeShares = async (e) => {
        e.preventDefault();
        await fetchTradeShares();
    }

    return (
        <form onSubmit={(e) => tradeShares(e)} className={"form__default"}>
            <input className={"input__default"} {...amount} type={"number"} placeholder={"amount"}/>
            {shareError?.amount && <div className={"cell__error"}>{shareError?.amount}</div>}
            <button className={"button__submit"}>{tradeType.value}</button>
            {shareError?.detail && <div className={"cell__error"}>{shareError?.detail}</div>}
            {shareError?.error && <div className={"cell__error"}>{shareError?.error}</div>}
        </form>
    );
};

export default BuyCurrentCompanyShares;