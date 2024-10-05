import React, {useEffect, useState} from 'react';
import {useFetching} from "../../hooks/useFetching";
import CompaniesService from "../../API/CompaniesService";
import AdaptiveLoading from "../../components/UI/AdaptiveLoading";
import BlankResult from "../../components/UI/BlankResult/BlankResult";

const UserCompaniesRecipes = () => {
    const [recipes, setRecipes] = useState();
    const [fetchCompaniesRecipes, isRecipesLoading] = useFetching(async () => {
        return await CompaniesService.getCompaniesRecipes();
    })

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
    //unused - recipe.company_type
    return (
        <div className={"profile__content__list"}>
            {recipes.length > 0 ? (recipes.map((recipe, index) => (
                <div className={"content__list__item"} key={index}>
                    <div className={"content__header"}>{recipe.type_display}</div>
                    <div className={"content__ingredient__list"}>
                        {recipe.ingredients.map((ingredient) => (
                            <div className={"ingredient__item"} key={ingredient.type}>
                                <div className={"ingredient__amount"}>{ingredient.amount}</div>
                                <div className={"ingredient__name"}>{ingredient.type_display}</div>
                            </div>
                        ))}
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