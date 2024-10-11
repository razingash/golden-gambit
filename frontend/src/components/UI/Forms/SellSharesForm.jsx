import React from 'react';
import useInput from "../../../hooks/useInput";
import {useFetching} from "../../../hooks/useFetching";
import CompaniesService from "../../../API/CompaniesService";

const SellSharesForm = ({ticker}) => {
    const amount = useInput('');
    const price = useInput('');
    const sharesType = useInput(1);

    const sharesTypes = {"ordinary": 1, "preffered": 1}

    const [fetchSellShares, ,sellSharesError] = useFetching(async () => {
        return await CompaniesService.sellUserShares(ticker, sharesType.value, amount.value, price.value)
    })

    const sellShares = async (e) => {
        e.preventDefault();
        await fetchSellShares();
    }

    return (
        <form onSubmit={(e) => sellShares(e)} className={"form__default"}>
            <input className={"input__default"} {...amount} type={"number"} placeholder={"amount"}/>
            {sellSharesError?.amount && <div className={"cell__error"}>{sellSharesError?.amount}</div>}
            <input className={"input__default"} {...price} type={"price"} placeholder={"price"}/>
            {sellSharesError?.price && <div className={"cell__error"}>{sellSharesError?.price}</div>}
            <select {...sharesTypes} onChange={(e) => sharesType.onChange(e)}>
                {Object.entries(sharesTypes).map(([shares, type]) => (
                    <option key={shares} value={type}>{shares}</option>
                ))}
            </select>
            {sellSharesError?.detail && <div className={"cell__error"}>{sellSharesError?.detail}</div>}
            <button className={"button__submit"}>sell</button>
        </form>
    );
};

export default SellSharesForm;