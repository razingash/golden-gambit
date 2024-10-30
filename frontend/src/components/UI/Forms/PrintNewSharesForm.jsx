import React from 'react';
import {useFetching} from "../../../hooks/useFetching";
import CompaniesService from "../../../API/CompaniesService";
import useInput from "../../../hooks/useInput";
import {selectSharesType} from "../../../functions/utils";

const PrintNewSharesForm = ({ticker, setCompanies}) => {
    const amount = useInput('');
    const price = useInput('');
    const sharesType = useInput(1);

    const [fetchNewShares, , newSharesError] = useFetching(async () => {
        return await CompaniesService.printNewCompanyShares(ticker, +sharesType.value, amount.value, price.value)
    }, 1500)

    const printNewShares = async (e) => {
        e.preventDefault();
        const responseData = await fetchNewShares();

        if (responseData) {
            setCompanies((prevCompanies) => prevCompanies.map((company) => {
                if (company.ticker === ticker) {
                    if (+sharesType.value === 1) {
                        return {...company, co_shares: +company.co_shares + +amount.value};
                    } else {
                        return {...company, cp_shares: +company.cp_shares + +amount.value};
                    }
                }
                return company;
            }));
        }
    }

    return (
        <form onSubmit={(e) => printNewShares(e)} className={"form__default"}>
            <input className={"input__default"} {...amount} type={"number"} placeholder={"amount"}/>
            {newSharesError?.amount && <div className={"cell__error"}>{newSharesError?.amount}</div>}
            <input className={"input__default"} {...price} type={"number"} placeholder={"price per share"}/>
            {newSharesError?.price && <div className={"cell__error"}>{newSharesError?.price}</div>}
            <select className={"select__default"} {...selectSharesType} onChange={(e) => sharesType.onChange(e)}>
                {Object.entries(selectSharesType).map(([shares, type]) => (
                    <option className={"option__default"} key={shares} value={type}>{shares}</option>
                ))}
            </select>
            {newSharesError?.detail && <div className={"cell__error"}>{newSharesError?.detail}</div>}
            <button className={"button__submit"}>print</button>
        </form>
    );
};

export default PrintNewSharesForm;