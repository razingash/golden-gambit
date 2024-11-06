import React from 'react';
import useInput from "../../../hooks/useInput";
import {useFetching} from "../../../hooks/useFetching";
import StockServices from "../../../API/StockServices";

const GlobalBuyCurrentCompanyShares = ({shares, onClose, setShares}) => {
    const amount = useInput('');
    const tradeType = useInput('buy');

    const [fetchTradeShares, isTradeLoading, shareError] = useFetching(async () => {
        return await StockServices.tradeShares(shares.ticker, shares.id, shares.shares_type, amount.value, shares.price)
    }, 0, 1000)

    const tradeShares = async (e) => {
        e.preventDefault();
        await fetchTradeShares();

        if (!isTradeLoading) {
            setShares(prevShares =>
                prevShares.map(share => {
                    if (share.id === shares.id) {
                        const updatedAmount = share.amount - parseInt(amount.value, 10);
                        return { ...share, amount: updatedAmount };
                    }
                    return share;
                })
            );
            onClose();
        }
    }

    return (
         <div className={"global__container"}>
            <div className={"form__global"}>
                <div className={"area__close"} onClick={onClose}><div className="cross"></div></div>
                <div className={"container__header_1 mod_width"}>
                    buy shares for {shares.price} {shares.shares_type === 1 ? "silver" : "gold"}
                </div>
                <form onSubmit={(e) => tradeShares(e)} className={"form__default"}>
                    <input className={"input__default"} {...amount} type={"number"} placeholder={"amount"}/>
                    {shareError?.amount && <div className={"cell__error"}>{shareError?.amount}</div>}
                    <button className={"button__submit"}>{tradeType.value}</button>
                    {shareError?.detail && <div className={"cell__error"}>{shareError?.detail}</div>}
                    {shareError?.error && <div className={"cell__error"}>{shareError?.error}</div>}
                </form>
            </div>
         </div>
    );
};

export default GlobalBuyCurrentCompanyShares;