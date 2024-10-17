import React from 'react';
import useInput from "../../../hooks/useInput";
import {useFetching} from "../../../hooks/useFetching";
import CompaniesService from "../../../API/CompaniesService";
import {useParams} from "react-router-dom";

const UpdateCompanyForm = ({baseName, baseDividendes, setCompanyData}) => {
    const {ticker} = useParams();
    const name = useInput(baseName);
    const dividendesPercent = useInput(baseDividendes);

    const [fetchUpdateCompany, ,updateError] = useFetching(async (requestData) => {
        return await CompaniesService.changeUserCompany(ticker, requestData)
    })

    const createRequestUpdateData = () => {
        const data = {}

        if (name.value !== baseName) {
            data.name = name.value;
        }

        if (dividendesPercent.value !== baseDividendes) {
            data.dividendes_percent = dividendesPercent.value;
        }

        return data
    }

    const updateCompany = async (e) => {
        e.preventDefault();
        const responseData = createRequestUpdateData();

        if (Object.keys(responseData).length > 0) {
            const updatedData = await fetchUpdateCompany(responseData);

            if (updatedData) {
                setCompanyData(prev => ({...prev, ...updatedData}))
            }
        }
    }

    return (
        <>
        <div className={"container__header_1"}>change company</div>
        <form className={"form__default"} onSubmit={(e) => updateCompany(e)}>
            <input {...name} type={"text"} placeholder={"company name"}/>
            {updateError?.name && <div className={"cell__error"}>{updateError?.name}</div>}
            <input {...dividendesPercent} type={"text"} placeholder={"dividendes %"}/>
            {updateError?.dividendes_percent && <div className={"cell__error"}>{updateError?.dividendes_percent}</div>}
            <button className={"button__submit"}>Submit</button>
            {updateError?.detail && <div className={"cell__error"}>{updateError?.detail}</div>}
            {updateError?.error && <div className={"cell__error"}>{updateError?.error}</div>}
        </form>
        </>
    );
};

export default UpdateCompanyForm;