import React, {useEffect, useState} from 'react';
import {useFetching} from "../hooks/useFetching";
import LawsService from "../API/LawsService";
import "../styles/laws_news.css"
import BlankResult from "../components/UI/BlankResult/BlankResult";
import AdaptiveLoading from "../components/UI/AdaptiveLoading";

const Laws = () => {
    const [laws, setLaws] = useState([]);
    const [fetchLaws, isLawsLoading] = useFetching(async () => {
        return await LawsService.getLawsList();
    })

    useEffect( () => {
        const loadLaws = async () => {
            if (!isLawsLoading && laws.length === 0) {
                const data = await fetchLaws();
                data && setLaws(data.data);
            }
        };
        void loadLaws();
    }, [fetchLaws, laws.length, isLawsLoading])

    if (isLawsLoading) {
        return <div className={"global__loading"}><AdaptiveLoading/></div>
    }

    if (!laws) {
        return <BlankResult title={"Server Error 502"} info={"no response was received from the server"}/>
    }

    return (
        <div className={"section__main"}>
            <div className={"field__laws"}>
                <div className={"laws__list"}>
                    {laws.length > 0 ? (laws.map((law) => (
                        <div className={"laws__item"} key={law.title}>
                            <div className={"law__title"}>{law.title}</div>
                            <div className={"law__description"}>{law.description}</div>
                            <div className={"law__limits"}>
                                <div>{law.since}</div>
                                <div >{law.to}</div>
                            </div>
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