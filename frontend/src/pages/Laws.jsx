import React, {useEffect, useState} from 'react';
import {useFetching} from "../hooks/useFetching";
import LawsService from "../API/LawsService";
import "../styles/laws_news.css"
import BlankResult from "../components/UI/BlankResult/BlankResult";

const Laws = () => {
    const [laws, setLaws] = useState([]);
    const [fetchLaws, isLawsLoading] = useFetching(async () => {
        return await LawsService.getLawsList();
    })

    useEffect( () => {
        const loadLaws = async () => {
            const laws = await fetchLaws();
            laws && setLaws(laws.data);
        };
        void loadLaws();
    }, [isLawsLoading])

    return (
        <div className={"section__main"}>
            <div className={"field__laws"}>
                <div className={"laws__list"}>
                    {laws.length > 0 ? (laws.map((law) => (
                        <div className={"laws__item"} key={law.title}>
                            <div className={"law__title"}>{law.title}</div>
                            <div className={"law__description"}>{law.description}</div>
                            <div className={"law__limits"}>
                                <div className={"law__start"}>{law.since}</div>
                                <div className={"law__end"}>{law.to}</div>
                            </div>
                            <div className={"law__is-actual"}>{law.isActual}</div>
                        </div>
                    ))) : (
                        <BlankResult title={"Lawless lands"} info={"no laws have been passed yet"}/>
                    )}
                </div>
            </div>
        </div>
    );
};

export default Laws;