import React from 'react';
import useInput from "../../hooks/useInput";
import {useFetching} from "../../hooks/useFetching";
import StockServices from "../../API/StockServices";

const TradeGold = () => {
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
        <div className={"field__gold_trade"}>
            <form onSubmit={tradeGold} className={"gold_trade__form"}>
                <input className={"input__stock"} {...amount} type={"number"} placeholder={"amount"}/>
                <select {...tradingTypes} onChange={(e) => tradeType.onChange(e)}>
                    {Object.entries(tradingTypes).map(([trade, type]) => (
                        <option key={trade} value={type}>{trade}</option>
                    ))}
                </select>
                {goldTradeError && <div className={"cell__error"}>{goldTradeError?.amount} {goldTradeError?.error}</div>}
                <button className={"button__submit"}>submit</button>
            </form>
        </div>
    );
};

export default TradeGold;