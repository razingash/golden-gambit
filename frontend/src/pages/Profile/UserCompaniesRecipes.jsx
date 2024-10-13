import React, {useEffect, useState} from 'react';
import {useFetching} from "../../hooks/useFetching";
import CompaniesService from "../../API/CompaniesService";
import AdaptiveLoading from "../../components/UI/AdaptiveLoading";
import BlankResult from "../../components/UI/BlankResult/BlankResult";
import {decodeCompanyType} from "../../functions/utils";
import UserService from "../../API/UserService";
import GlobalMergeCompaniesForm from "../../components/UI/Forms/GlobalMergeCompaniesForm";

const UserCompaniesRecipes = () => {
    const [recipes, setRecipes] = useState();
    const [fetchCompaniesRecipes, isRecipesLoading] = useFetching(async () => {
        return await CompaniesService.getCompaniesRecipes();
    })
    const [userCompanies, setUserCompanies] = useState([]);
    const [fetchUserCompanies, isUserCompaniesLoading] = useFetching(async () => {
        return await UserService.getUserCompanies(1,1000, ['type', 'name', 'ticker'])
    })
    const [isFormSpawned, setForm] = useState(false);
    const [selectedRecipe, setSelectedRecipe] = useState(null);

    const areAllIngredientsAvailable = (recipe) => {
        return recipe.ingredients.every((ingredient) => {
            const filteredCompanies = userCompanies.filter(company => company.type === ingredient.type);
            return filteredCompanies.length >= ingredient.amount;
        });
    };

    const spawnForm = (recipe) => {
        setForm(!isFormSpawned)
        setSelectedRecipe(recipe)
    }

    const closeForm = () => {
        setForm(false);
        setSelectedRecipe(null);
    };

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
            {recipes.length > 0 ? ( recipes.map((recipe, index) =>
                <div className={"container__default"} key={index}>
                    <div className={"container__header_1 content__header"}>{decodeCompanyType(recipe.company_type)}</div>
                    <div className={"content__ingredient__list"}>
                        {recipe.ingredients.map((ingredient) => (
                            <div className={"ingredient__item"} key={ingredient.type}>
                                <div className={"ingredient__info"}>
                                    {ingredient.amount} {decodeCompanyType(ingredient.type)}
                                </div>
                            </div>
                        ))}
                        {areAllIngredientsAvailable(recipe) && (
                            <button className={"button__submit"} onClick={() => spawnForm(recipe)}>transmutate</button>
                        )}
                    </div>
                </div>
            )) : (
                <BlankResult title={"Server problem"} info={"Data hasn't been initialized yet"}/>
            )}
            {isFormSpawned && <GlobalMergeCompaniesForm recipe={selectedRecipe} userCompanies={userCompanies} onClose={closeForm}/>}
        </div>
    );
};

export default UserCompaniesRecipes;