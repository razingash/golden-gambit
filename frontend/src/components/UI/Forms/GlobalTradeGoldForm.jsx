import React from 'react';
import useInput from "../../../hooks/useInput";
import {useFetching} from "../../../hooks/useFetching";
import StockServices from "../../../API/StockServices";
import {selectTradingType} from "../../../functions/utils";

const GlobalTradeGoldForm = ({onClose}) => {
    const amount = useInput('');
    const tradeType = useInput('buy');
    const [fetchGoldTrade, , goldTradeError] = useFetching(async () => {
        return await StockServices.tradeGold(tradeType.value, amount.value)
    }, 500, 1000)

    const tradeGold = async (e) => {
        e.preventDefault();
        await fetchGoldTrade();
    }

    return (
        <div className={"global__container"}>
            <div className={"form__global"}>
                <div className={"area__close"} onClick={onClose}><div className="cross"></div></div>
                <div className={"container__header_1 mod_width"}>Trade Gold</div>
                <form onSubmit={tradeGold} className={"gold_trade__form"}>
                    <input className={"input__default"} {...amount} type={"number"} placeholder={"amount"}/>
                    {goldTradeError?.amount && <div className={"cell__error"}>{goldTradeError?.amount}</div>}
                    <select className={"select__default-2"} {...selectTradingType} onChange={(e) => tradeType.onChange(e)}>
                        {Object.entries(selectTradingType).map(([trade, type]) => (
                            <option className={"option__default-2"} key={trade} value={type}>{trade}</option>
                        ))}
                    </select>
                    {goldTradeError?.error && <div className={"cell__error"}>{goldTradeError?.error}</div>}
                    <button className={"button__submit"}>submit</button>
                </form>
            </div>
        </div>
    );
};

export default GlobalTradeGoldForm;