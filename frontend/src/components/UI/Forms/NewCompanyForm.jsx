import React from 'react';
import useInput from "../../../hooks/useInput";
import {useFetching} from "../../../hooks/useFetching";
import CompaniesService from "../../../API/CompaniesService";
import {useNavigate} from "react-router-dom";
import {selectCompanyType} from "../../../functions/utils";

const NewCompanyForm = () => {
    const navigate = useNavigate();
    const companyType = useInput(1)
    const ticker = useInput('')
    const name = useInput('')
    const sharesAmount = useInput('')
    const preferredSharesAmount = useInput('')
    const dividendesPercent = useInput('')

    const [fetchNewCompany, ,formError] = useFetching(async () => {
        return await CompaniesService.createNewCompany(+companyType.value, ticker.value, name.value, sharesAmount.value,
            preferredSharesAmount.value, dividendesPercent.value)
    }, 0, 1000)

    const createNewCompany = async (e) => {
        e.preventDefault();
        const newCompany = await fetchNewCompany();
        if (newCompany?.ticker) {
            navigate(`/companies/${newCompany.ticker}/`);
        }
    }

    return (
        <div className={"container__default flexible_container"}>
            <div className={"container__header_1"}>create new company</div>
            <form onSubmit={(e) => createNewCompany(e)} className={"form__create_company"}>
                <select className={"select__default"} value={companyType.value} onChange={(e) => companyType.onChange(e)}>
                    {Object.entries(selectCompanyType).map(([company, type]) => (
                        <option className={"option__default"} key={company} value={type}>{company}</option>
                    ))}
                </select>
                {formError?.type && <div className={"cell__error"}>{formError?.type}</div>}
                <input className={"input__default"} {...name} type={"text"} placeholder={"name"}/>
                {formError?.name && <div className={"cell__error"}>{formError?.name}</div>}
                <input className={"input__default"} {...ticker} type={"text"} placeholder={"ticker"}/>
                {formError?.ticker && <div className={"cell__error"}>{formError?.ticker}</div>}
                <input className={"input__default"} {...sharesAmount} type={"number"} placeholder={"shares amount"}/>
                {formError?.shares_amount && <div className={"cell__error"}>{formError?.shares_amount}</div>}
                <input className={"input__default"} {...preferredSharesAmount} type={"number"} placeholder={"preferred shares amount"}/>
                {formError?.preferred_shares_amount && <div className={"cell__error"}>{formError?.preferred_shares_amount}</div>}
                <input className={"input__default"} {...dividendesPercent} type={"number"} placeholder={"dividendes %"}/>
                {formError?.dividendes_percent && <div className={"cell__error"}>{formError?.dividendes_percent}</div>}
                <button className={"button__submit"}>Submit</button>
                {formError?.detail && <div className={"cell__error"}>{formError?.detail}</div>}
                {formError?.error && <div className={"cell__error"}>{formError?.error}</div>}
            </form>
        </div>
    );
};

export default NewCompanyForm;