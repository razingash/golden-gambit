import React from 'react';
import useInput from "../../../hooks/useInput";
import {useFetching} from "../../../hooks/useFetching";
import CompaniesService from "../../../API/CompaniesService";
import {selectSharesType} from "../../../functions/utils";

const GlobalSellSharesForm = ({ticker, setShares, onClose}) => {
    const amount = useInput('');
    const price = useInput('');
    const sharesType = useInput(1);

    const [fetchSellShares, ,sellSharesError] = useFetching(async () => {
        return await CompaniesService.sellUserShares(ticker, +sharesType.value, amount.value, price.value)
    }, 0, 1000)

    const sellShares = async (e) => {
        e.preventDefault();
        const responseData = await fetchSellShares();

        if (responseData) {
            setShares((prevShares) => prevShares.map((share) => {
                if (share.ticker === ticker) {
                    if (+sharesType.value === 1) {
                        return {...share, shares_amount: share.shares_amount - amount.value};
                    } else {
                        return {...share, preferred_shares_amount: share.preferred_shares_amount - amount.value};
                    }
                }
                return share;
            }));
        }
    }

    return (
        <div className={"global__container"}>
            <div className={"form__global"}>
                <div className={"area__close"} onClick={onClose}><div className="cross"></div></div>
                <div className={"container__header_1 mod_width"}>{ticker}</div>
                <form onSubmit={(e) => sellShares(e)} className={"form__default"}>
                    <input className={"input__default"} {...amount} type={"number"} placeholder={"amount"}/>
                    {sellSharesError?.amount && <div className={"cell__error"}>{sellSharesError?.amount}</div>}
                    <input className={"input__default"} {...price} type={"price"} placeholder={"price"}/>
                    {sellSharesError?.price && <div className={"cell__error"}>{sellSharesError?.price}</div>}
                    <select className={"select__default"} {...selectSharesType} onChange={(e) => sharesType.onChange(e)}>
                        {Object.entries(selectSharesType).map(([shares, type]) => (
                            <option className={"option__default"} key={shares} value={type}>{shares}</option>
                        ))}
                    </select>
                    {sellSharesError?.detail && <div className={"cell__error"}>{sellSharesError?.detail}</div>}
                    {sellSharesError?.error && <div className={"cell__error"}>{sellSharesError?.error}</div>}
                    <button className={"button__submit"}>sell</button>
                </form>
            </div>
        </div>
    );
};

export default GlobalSellSharesForm;