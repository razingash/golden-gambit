import React from 'react';
import useInput from "../../../hooks/useInput";
import {useFetching} from "../../../hooks/useFetching";
import StockServices from "../../../API/StockServices";
/*
Before making this component:
sorting in the display of the list of shares and automatic price calculation depending on the quantity
backend
change the system of selling shares so that they are bought in batches
*/
const BuyShares = ( {ticker, sharesType} ) => {
    const amount = useInput('');
    const tradeType = useInput('buy');

    const [fetchTradeShares, ,shareError] = useFetching(async () => {
        return await StockServices.tradeShares(ticker, sharesType, amount.value, 0)
    })

    const tradeShares = async (e) => {
        e.preventDefault();
        await fetchTradeShares();
    }

    return (
        <form onSubmit={(e) => tradeShares(e)} className={"form_trading"}>
            <input className={"input__stock"} {...amount} type={"number"} placeholder={"amount"}/>
            {shareError?.amount && <div className={"cell__error"}>{shareError?.amount}</div>}
            <input className={"input__stock"} {...ticker} type={"text"} placeholder={"ticker"}/>
            {shareError?.ticker && <div className={"cell__error"}>{shareError?.ticker}</div>}
            {shareError?.detail && <div className={"cell__error"}>{shareError?.detail}</div>}
            <button className={"button__submit"}>{tradeType.value}</button>
        </form>
    );
};

export default BuyShares;