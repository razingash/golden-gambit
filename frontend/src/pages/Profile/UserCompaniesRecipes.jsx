import React, {useEffect, useState} from 'react';
import {useFetching} from "../../hooks/useFetching";
import CompaniesService from "../../API/CompaniesService";
import AdaptiveLoading from "../../components/UI/AdaptiveLoading";
import BlankResult from "../../components/UI/BlankResult/BlankResult";
import {decodeCompanyType} from "../../functions/utils";
import UserService from "../../API/UserService";
import SelectCompaniesForm from "../../components/UI/Forms/MergeCompanies/SelectCompaniesForm";
import MergeCompaniesForm from "../../components/UI/Forms/MergeCompanies/MergeCompaniesForm";

const UserCompaniesRecipes = () => {
    const [recipes, setRecipes] = useState();
    const [fetchCompaniesRecipes, isRecipesLoading] = useFetching(async () => {
        return await CompaniesService.getCompaniesRecipes();
    })
    const [userCompanies, setUserCompanies] = useState([]);
    const [fetchUserCompanies, isUserCompaniesLoading] = useFetching(async () => {
        return await UserService.getUserCompanies(1,1000, ['type', 'name', 'ticker'])
    })
    const [selectedCompanies, setSelectedCompanies] = useState([]);

    const handleSelectCompanies = (index, companies) => {
        const updateSelected = [...selectedCompanies];
        updateSelected[index] = companies;
        setSelectedCompanies(updateSelected);
    }

    useEffect(() => {
        const loadData = async () => {
            const data = await fetchUserCompanies();
            data && setUserCompanies(data.data);
        }
        void loadData();
    }, [isUserCompaniesLoading])

    useEffect(() => {
        const loadData = async () => {
            const data = await fetchCompaniesRecipes();
            data && setRecipes(data)
        }
        void loadData();
    }, [isRecipesLoading])

    if (!recipes) {
        return <AdaptiveLoading/>
    }

    return (
        <div className={"area__row"}>
            {recipes.length > 0 ? (recipes.map((recipe, index) => (
                <div className={"container__default"} key={index}>
                    <div className={"container__header_1 content__header"}>{decodeCompanyType(recipe.company_type)}</div>
                    <div className={"content__ingredient__list"}>
                        {recipe.ingredients.map((ingredient, ingredientIndex) => (
                            <div className={"ingredient__item"} key={ingredient.type}>
                                <div className={"ingredient__info"}>{ingredient.amount} {decodeCompanyType(ingredient.type)}</div>
                                <SelectCompaniesForm userCompanies={userCompanies} companyType={ingredient.type}
                                                     sacrificesAmount={ingredient.amount} onSelectCompanies={(companies) => handleSelectCompanies(ingredientIndex, companies)}/>
                            </div>
                        ))}
                        <MergeCompaniesForm selectedCompanies={selectedCompanies.flat()} companyType={recipe.company_type} />
                    </div>
                </div>
                ))
            ) : (
                <BlankResult title={"Server problem"} info={"Data hasn't been initialized yet"}/>
            )}
        </div>
    );
};

export default UserCompaniesRecipes;