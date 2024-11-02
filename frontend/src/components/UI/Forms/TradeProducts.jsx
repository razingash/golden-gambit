import React from 'react';
import {useFetching} from "../../../hooks/useFetching";
import StockServices from "../../../API/StockServices";
import useInput from "../../../hooks/useInput";
import {selectTradingType} from "../../../functions/utils";

const TradeProducts = ( {productType} ) => {
    const amount = useInput('');
    const ticker = useInput('');
    const tradeType = useInput('buy');

    const [fetchTradeProducts, ,productsTradeError] = useFetching(async (productType) => {
        return await StockServices.tradeProducts(tradeType.value, ticker.value, amount.value, productType)
    })

    const tradeProducts = async (e, productType) => {
        e.preventDefault();
        await fetchTradeProducts(productType);
    }

    return (
        <form onSubmit={(e) => tradeProducts(e, productType)} className={"form__default"}>
            <input className={"input__default"} {...amount} type={"number"} placeholder={"amount"}/>
            {productsTradeError?.amount && <div className={"cell__error"}>{productsTradeError?.amount}</div>}
            <input className={"input__default"} {...ticker} type={"text"} placeholder={"ticker"}/>
            {productsTradeError?.ticker && <div className={"cell__error"}>{productsTradeError?.ticker}</div>}
            <select className={"select__default"} {...selectTradingType} onChange={(e) => tradeType.onChange(e)}>
                {Object.entries(selectTradingType).map(([trade, type]) => (
                    <option className={"option__default"} key={trade} value={type}>{trade}</option>
                ))}
            </select>
            {productsTradeError?.detail && <div className={"cell__error"}>{productsTradeError?.detail}</div>}
            <button className={"button__submit"}>{tradeType.value}</button>
        </form>
    );
};

export default TradeProducts;