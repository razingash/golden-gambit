import React, {useState} from 'react';
import useInput from "../../../hooks/useInput";
import UserService from "../../../API/UserService";
import {decodeCompanyType} from "../../../functions/utils";
import {useFetching} from "../../../hooks/useFetching";

const GlobalMergeCompaniesForm = ({recipe, userCompanies, onClose}) => {
    const [selectedCompanies, setSelectedCompanies] = useState([]);
    const ticker = useInput('')
    const name = useInput('')
    const dividendesPercent = useInput('')

    const [fetchMergedCommpany, , mergedCompanyError] = useFetching(async () => {
        return await UserService.megreCompanies(recipe.recipe, selectedCompanies.flat(), ticker.value,
            name.value, +dividendesPercent.value);
    }, 0, 1000)

    const handleCompanySelection = (ingredientIndex, companies) => {
        const updatedSelected = [...selectedCompanies];
        updatedSelected[ingredientIndex] = companies;
        setSelectedCompanies(updatedSelected);
    };

    const mergeCompany = async (e) => {
        e.preventDefault();
        await fetchMergedCommpany();
    }

    const renderSelectCompanies = (ingredient, index) => {
        const filteredCompanies = userCompanies.filter(company => company.type === ingredient.type);
        if (filteredCompanies.length === 0) {
            return <div key={index}>Not enough companies for {decodeCompanyType(ingredient.type)}</div>;
        }

        return (
            <div className={"cell__column"} key={ingredient.type + recipe.recipe}>
                {Array.from({ length: ingredient.amount }).map((_, companyIndex) => (
                    <select className={"select__default-2"} key={companyIndex} value={selectedCompanies[index]?.[companyIndex] || ''}
                        onChange={(e) => {
                            const updatedCompanies = [...(selectedCompanies[index] || [])];
                            updatedCompanies[companyIndex] = e.target.value;
                            handleCompanySelection(index, updatedCompanies);
                        }}
                    >
                        <option className={"option__default-2"} value="" disabled>Select company</option>
                        {filteredCompanies.map((company) => (
                            <option className={"option__default-2"} key={company.ticker} value={company.ticker}>{company.name} ({company.ticker})</option>
                        ))}
                    </select>
                ))}
            </div>
        )
    }

    return (
        <div className={"global__container"}>
            <div className={"form__global"}>
                <div className={"area__close"} onClick={onClose}><div className="cross"></div></div>
                <form onSubmit={(e) => mergeCompany(e)} className={"form__default-2"}>
                    {recipe.ingredients.map((ingredient, index) => renderSelectCompanies(ingredient, index))}
                    <input className={"input__default"} {...name} type={"text"} placeholder={"name"}/>
                    {mergedCompanyError?.name && <div className={"cell__error"}>{mergedCompanyError?.name}</div>}
                    <input className={"input__default"} {...ticker} type={"text"} placeholder={"ticker"}/>
                    {mergedCompanyError?.ticker && <div className={"cell__error"}>{mergedCompanyError?.ticker}</div>}
                    <input className={"input__default"} {...dividendesPercent} type={"text"} placeholder={"dividendes %"}/>
                    {mergedCompanyError?.dividendes_percent && <div className={"cell__error"}>{mergedCompanyError?.dividendes_percent}</div>}
                    <button className={"button__submit"}>Submit</button>
                    {mergedCompanyError?.detail && <div className={"cell__error"}>{mergedCompanyError?.detail}</div>}
                    {mergedCompanyError?.error && <div className={"cell__error"}>{mergedCompanyError?.error}</div>}
                </form>
            </div>
        </div>
    );
};

export default GlobalMergeCompaniesForm;