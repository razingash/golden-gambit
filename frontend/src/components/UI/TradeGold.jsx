import React from 'react';
import useInput from "../../hooks/useInput";
import {useFetching} from "../../hooks/useFetching";
import StockServices from "../../API/StockServices";

const TradeGold = () => {
    const amount = useInput('');
    const tradeType = useInput('buy');
    const [fetchGoldTrade, isGoldTradeLoading] = useFetching(async () => {
        return await StockServices.tradeGold(tradeType.value, amount)
    })

    const tradingTypes = { "purchase": "buy", "sale": "sell" }

    const tradeGold = async (e) => {
        e.preventDefault();
        const error = await fetchGoldTrade();
        if (error) { // improve
            console.log('tradeGold error')
        }
    }

    return (
        <div className={"field__gold_trade"}>
            <form onSubmit={tradeGold} className={"gold_trade__form"}>
                <input className={"input__stock"} {...amount} type={"text"} placeholder={"amount"}/>
                <select {...tradingTypes}>
                    {Object.entries(tradingTypes).map(([trade, type]) => (
                        <option key={trade} value={type}>{trade}</option>
                    ))}
                </select>
                <button className={"button__submit"}>submit</button>
            </form>
        </div>
    );
};

export default TradeGold;