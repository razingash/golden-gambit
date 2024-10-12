import React from 'react';
import useInput from "../../../../hooks/useInput";
import {useFetching} from "../../../../hooks/useFetching";
import UserService from "../../../../API/UserService";

const MergeCompaniesForm = ({selectedCompanies, companyType}) => {
    const ticker = useInput('')
    const name = useInput('')
    const sharesAmount = useInput('')
    const preferredSharesAmount = useInput('')
    const dividendesPercent = useInput('')

    const [fetchMergedCommpany, , formError] = useFetching(async () => {
        return await UserService.megreCompanies(companyType, selectedCompanies, ticker.value, name.value,
            sharesAmount.value, preferredSharesAmount.value, dividendesPercent.value);
    })

    const mergeCompany = async (e) => {
        e.preventDefault();
        await fetchMergedCommpany();
    }

    return (
        <form onSubmit={(e) => mergeCompany(e)} className={"form__default"}>
            <input className={"input__create_company"} {...name} type={"text"} placeholder={"name"}/>
            {formError?.ticker && <div className={"cell__error"}>{formError?.name}</div>}
            <input className={"input__create_company"} {...ticker} type={"text"} placeholder={"ticker"}/>
            {formError?.ticker && <div className={"cell__error"}>{formError?.ticker}</div>}
            <input className={"input__create_company"} {...sharesAmount} type={"text"} placeholder={"shares amount"}/>
            {formError?.ticker && <div className={"cell__error"}>{formError?.shares_amount}</div>}
            <input className={"input__create_company"} {...preferredSharesAmount} type={"text"} placeholder={"preferred shares amount"}/>
            {formError?.ticker && <div className={"cell__error"}>{formError?.preferred_shares_amount}</div>}
            <input className={"input__create_company"} {...dividendesPercent} type={"text"} placeholder={"dividendes %"}/>
            {formError?.ticker && <div className={"cell__error"}>{formError?.ticker}</div>}
            <button className={"button__submit"}>Submit</button>
            {formError?.detail && <div className={"cell__error"}>{formError?.detail}</div>}
            {formError?.error && <div className={"cell__error"}>{formError?.error}</div>}
        </form>
    );
};

export default MergeCompaniesForm;