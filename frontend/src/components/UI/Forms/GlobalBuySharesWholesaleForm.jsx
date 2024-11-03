import React from 'react';
import {useFetching} from "../../../hooks/useFetching";
import StockServices from "../../../API/StockServices";
import useInput from "../../../hooks/useInput";

const GlobalBuySharesWholesaleForm = ({shares, onClose}) => {
    const desiredAmount = useInput('');
    const reservedMoney = useInput('');
    const [fetchWholesalePurchase, ,wholesalePurchaseError] = useFetching(async () => {
        return await StockServices.buySharesWholesale(shares.ticker, shares.sharesType, desiredAmount.value, reservedMoney.value);
    }, 0, 1000)

    const wholesalePurchase = async (e) => {
        e.preventDefault();
        await fetchWholesalePurchase();
    }

    return (
        <div className={"global__container"}>
            <div className={"form__global"}>
                <div className={"area__close"} onClick={onClose}><div className="cross"></div></div>
                <div className={"container__header_1 mod_width"}>{shares.name}</div>
                <form onSubmit={(e) => wholesalePurchase(e)} className={"form__default"}>
                    <input className={"input__default"} {...desiredAmount} type={"number"} placeholder={"amount"}/>
                    {wholesalePurchaseError?.desired_quantity && <div className={"cell__error"}>{wholesalePurchaseError?.desired_quantity}</div>}
                    <input className={"input__default"} {...reservedMoney} type={"number"} placeholder={"reserved money"}/>
                    {wholesalePurchaseError?.reserved_money && <div className={"cell__error"}>{wholesalePurchaseError?.reserved_money}</div>}
                    <button className={"button__submit"}>buy</button>
                </form>
            </div>
        </div>
    );
};

export default GlobalBuySharesWholesaleForm;