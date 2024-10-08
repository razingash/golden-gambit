import React from 'react';
import useInput from "../../../../hooks/useInput";
import {useFetching} from "../../../../hooks/useFetching";
import CompaniesService from "../../../../API/CompaniesService";

const NewCompanyForm = () => { // improve type selection and styles
    const type = useInput('')
    const ticker = useInput('')
    const name = useInput('')
    const sharesAmount = useInput('')
    const preferredSharesAmount = useInput('')
    const dividendesPercent = useInput('')

    const [fetchNewCompany, ,formError] = useFetching(async () => {
        return await CompaniesService.createNewCompany(type.value, ticker.value, name.value, sharesAmount.value,
            preferredSharesAmount.value, dividendesPercent.value)
    })

    const createNewCompany = async (e) => {
        e.preventDefault();
        await fetchNewCompany();
    }

    return (
        <div className={"container__default"}>
            <div className={"container__header_1"}>create new company</div>
            <form onSubmit={(e) => createNewCompany(e)} className={"form__create_company"}>
                <input className={"input__create_company"} {...type} type={"text"} placeholder={"type REDO"}/>
                {formError?.type && <div className={"cell__error"}>{formError?.type}</div>}
                <input className={"input__create_company"} {...name} type={"text"} placeholder={"name"}/>
                {formError?.name && <div className={"cell__error"}>{formError?.name}</div>}
                <input className={"input__create_company"} {...ticker} type={"text"} placeholder={"ticker"}/>
                {formError?.ticker && <div className={"cell__error"}>{formError?.ticker}</div>}
                <input className={"input__create_company"} {...sharesAmount} type={"number"} placeholder={"shares amount"}/>
                {formError?.shares_amount && <div className={"cell__error"}>{formError?.shares_amount}</div>}
                <input className={"input__create_company"} {...preferredSharesAmount} type={"number"} placeholder={"preffered shares amount"}/>
                {formError?.preferred_shares_amount && <div className={"cell__error"}>{formError?.preferred_shares_amount}</div>}
                <input className={"input__create_company"} {...dividendesPercent} type={"number"} placeholder={"dividendes %"}/>
                {formError?.dividendes_percent && <div className={"cell__error"}>{formError?.dividendes_percent}</div>}
                <button className={"button__submit"}>Submit</button>
                {formError?.detail && <div className={"cell__error"}>{formError?.detail}</div>}
                {formError?.error && <div className={"cell__error"}>{formError?.error}</div>}
            </form>
        </div>
    );
};

export default NewCompanyForm;