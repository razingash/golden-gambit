import React from 'react';
import useInput from "../../../hooks/useInput";
import {useFetching} from "../../../hooks/useFetching";
import StockServices from "../../../API/StockServices";

const TradeGoldForm = () => {
    const amount = useInput('');
    const tradeType = useInput('buy');
    const [fetchGoldTrade, , goldTradeError] = useFetching(async () => {
        return await StockServices.tradeGold(tradeType.value, amount.value)
    }, 1000)

    const tradingTypes = { "purchase": "buy", "sale": "sell" }

    const tradeGold = async (e) => {
        e.preventDefault();
        await fetchGoldTrade();
    }

    return (
        <form onSubmit={tradeGold} className={"gold_trade__form"}>
            <input className={"input__default"} {...amount} type={"number"} placeholder={"amount"}/>
            {goldTradeError?.amount && <div className={"cell__error"}>{goldTradeError?.amount}</div>}
            <select {...tradingTypes} onChange={(e) => tradeType.onChange(e)}>
                {Object.entries(tradingTypes).map(([trade, type]) => (
                    <option key={trade} value={type}>{trade}</option>
                ))}
            </select>
            {goldTradeError?.error && <div className={"cell__error"}>{goldTradeError?.error}</div>}
            <button className={"button__submit"}>submit</button>
        </form>
    );
};

export default TradeGoldForm;