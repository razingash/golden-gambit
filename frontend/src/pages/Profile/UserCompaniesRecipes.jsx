import React, {useEffect, useRef, useState} from 'react';
import {useFetching} from "../../hooks/useFetching";
import CompaniesService from "../../API/CompaniesService";
import AdaptiveLoading from "../../components/UI/AdaptiveLoading";
import BlankResult from "../../components/UI/BlankResult/BlankResult";
import {decodeCompanyType} from "../../functions/utils";
import UserService from "../../API/UserService";
import GlobalMergeCompaniesForm from "../../components/UI/Forms/GlobalMergeCompaniesForm";

const UserCompaniesRecipes = () => {
    const [recipes, setRecipes] = useState([]);
    const [userCompanies, setUserCompanies] = useState([]);
    const [fetchCompaniesRecipes, isRecipesLoading] = useFetching(async () => {
        return await CompaniesService.getCompaniesRecipes();
    })
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
            if (!isUserCompaniesLoading && userCompanies.length === 0) {
                const data = await fetchUserCompanies();
                data && setUserCompanies(data.data);
            }
        }
        void loadData();
    }, [isUserCompaniesLoading])

    const hasFetchedRecipes = useRef(false);
    useEffect(() => {
        // с этим компонентом происходит чертовщина - запрос для рецепта дублируется и из-за этого медленно грузится
        const loadData = async () => {// что-то не так с этим запросом - вместо двух раз 4 раза вызывается
            console.log(1)
            if (!isRecipesLoading && recipes.length === 0 && !hasFetchedRecipes.current) {
                hasFetchedRecipes.current = true;
                console.log(2)
                const data = await fetchCompaniesRecipes();
                data && setRecipes(data);
            }
        }
        void loadData();
    }, [isRecipesLoading])

    if (recipes.length === 0 && isRecipesLoading) {
        return <AdaptiveLoading/>
    }

    return (
        <div className={"area__column container__default"}>
            {recipes.length > 0 ? ( recipes.map((recipe) =>
                <div className={"container__default3"} key={recipe.recipe}>
                    <div className={"transmutation__header content__header"}>
                        <div className={"text__direct"}>{decodeCompanyType(recipe.company_type)}</div>
                        {areAllIngredientsAvailable(recipe) && (
                            <button className={"button__submit button__transmutation"} onClick={() => spawnForm(recipe)}>transmutate</button>
                        )}
                    </div>
                    <div className={"content__ingredient__list"}>
                        {recipe.ingredients.map((ingredient) => (
                            <div className={"ingredient__item"} key={ingredient.type}>
                                {ingredient.amount} {decodeCompanyType(ingredient.type)}
                            </div>
                        ))}
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