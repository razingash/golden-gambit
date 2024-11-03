import React from 'react';
import {useFetching} from "../../../hooks/useFetching";
import StockServices from "../../../API/StockServices";
import useInput from "../../../hooks/useInput";
import {decodeProductType, selectTradingType} from "../../../functions/utils";

const GlobalTradeProductsForm = ({productType, onClose}) => {
    const amount = useInput('');
    const ticker = useInput('');
    const tradeType = useInput('buy');

    const [fetchTradeProducts, ,productsTradeError] = useFetching(async (productType) => {
        return await StockServices.tradeProducts(tradeType.value, ticker.value, amount.value, productType)
    }, 0, 1000)

    const tradeProducts = async (e, productType) => {
        e.preventDefault();
        await fetchTradeProducts(productType);
    }

    return (
        <div className={"global__container"}>
            <div className={"form__global"}>
                <div className={"area__close"} onClick={onClose}><div className="cross"></div></div>
                <div className={"container__header_1 mod_width"}>{decodeProductType(productType)}</div>
                <form onSubmit={(e) => tradeProducts(e, productType)} className={"form__default-2"}>
                    <input className={"input__default"} {...amount} type={"number"} placeholder={"amount"}/>
                    {productsTradeError?.amount && <div className={"cell__error"}>{productsTradeError?.amount}</div>}
                    <input className={"input__default"} {...ticker} type={"text"} placeholder={"ticker"}/>
                    {productsTradeError?.ticker && <div className={"cell__error"}>{productsTradeError?.ticker}</div>}
                    <select className={"select__default-2"} {...selectTradingType} onChange={(e) => tradeType.onChange(e)}>
                        {Object.entries(selectTradingType).map(([trade, type]) => (
                            <option className={"option__default-2"} key={trade} value={type}>{trade}</option>
                        ))}
                    </select>
                    {productsTradeError?.detail && <div className={"cell__error"}>{productsTradeError?.detail}</div>}
                    <button className={"button__submit"}>{tradeType.value}</button>
                </form>
            </div>
        </div>
    );
};

export default GlobalTradeProductsForm;