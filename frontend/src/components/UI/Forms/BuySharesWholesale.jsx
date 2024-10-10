import React from 'react';
import {useFetching} from "../../../hooks/useFetching";
import StockServices from "../../../API/StockServices";
import useInput from "../../../hooks/useInput";

const BuySharesWholesale = ({ticker, sharesType}) => {
    const desiredAmount = useInput('');
    const reservedMoney = useInput('');
    const [fetchWholesalePurchase, ,wholesalePurchaseError] = useFetching(async () => {
        return await StockServices.buySharesWholesale(ticker, sharesType, desiredAmount.value, reservedMoney.value);
    })

    const wholesalePurchase = async (e) => {
        e.preventDefault();
        await fetchWholesalePurchase();
    }

    return (
        <form onSubmit={(e) => wholesalePurchase(e)} className={"form__default"}>
            <input className={"input__default"} {...desiredAmount} type={"number"} placeholder={"amount"}/>
            {wholesalePurchaseError?.desired_quantity && <div className={"cell__error"}>{wholesalePurchaseError?.desired_quantity}</div>}
            <input className={"input__default"} {...reservedMoney} type={"number"} placeholder={"reserved money"}/>
            {wholesalePurchaseError?.reserved_money && <div className={"cell__error"}>{wholesalePurchaseError?.reserved_money}</div>}
            <button className={"button__submit"}>buy</button>
        </form>
    );
};

export default BuySharesWholesale;