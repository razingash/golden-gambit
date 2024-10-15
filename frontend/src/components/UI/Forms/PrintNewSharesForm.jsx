import React from 'react';
import {useFetching} from "../../../hooks/useFetching";
import CompaniesService from "../../../API/CompaniesService";
import useInput from "../../../hooks/useInput";
import {sharesTypes} from "../../../functions/utils";

const PrintNewSharesForm = ({ticker}) => {
    const amount = useInput('');
    const price = useInput('');
    const sharesType = useInput(1);

    const [fetchNewShares, , newSharesError] = useFetching(async () => {
        return await CompaniesService.printNewCompanyShares(ticker, +sharesType.value, amount.value, price.value)
    })

    const printNewShares = async (e) => {
        e.preventDefault();
        await fetchNewShares();
    }

    return (
        <form onSubmit={(e) => printNewShares(e)} className={"form__default"}>
            <input className={"input__default"} {...amount} type={"number"} placeholder={"amount"}/>
            {newSharesError?.amount && <div className={"cell__error"}>{newSharesError?.amount}</div>}
            <input className={"input__default"} {...price} type={"number"} placeholder={"price per share"}/>
            {newSharesError?.price && <div className={"cell__error"}>{newSharesError?.price}</div>}
            <select className={"select__default"} {...sharesTypes} onChange={(e) => sharesType.onChange(e)}>
                {Object.entries(sharesTypes).map(([shares, type]) => (
                    <option className={"option__default"} key={shares} value={type}>{shares}</option>
                ))}
            </select>
            {newSharesError?.detail && <div className={"cell__error"}>{newSharesError?.detail}</div>}
            <button className={"button__submit"}>print</button>
        </form>
    );
};

export default PrintNewSharesForm;