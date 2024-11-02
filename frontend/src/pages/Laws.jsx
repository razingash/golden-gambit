import React, {useEffect, useState} from 'react';
import {useFetching} from "../hooks/useFetching";
import LawsService from "../API/LawsService";
import "../styles/laws_news.css"
import BlankResult from "../components/UI/BlankResult/BlankResult";
import AdaptiveLoading from "../components/UI/AdaptiveLoading";

const Laws = () => {
    const [laws, setLaws] = useState([]);
    const [fetchLaws, isLawsLoading, error] = useFetching(async () => {
        return await LawsService.getLawsList();
    })

    // WARGING: if you specify a function call depending on it, there will be many more unnecessary calls
    useEffect( () => { // the very minimum of calls in ALL CASES. if you use useCallback there will be 1 more
        const loadLaws = async () => { // 4 times (2)
            if (!isLawsLoading && laws.length === 0 && !error) { // 2 times(1)
                const data = await fetchLaws();
                data && setLaws(data.data);
            }
        };
        void loadLaws();
    }, [isLawsLoading, error])

    if (isLawsLoading) {
        return <div className={"global__loading"}><AdaptiveLoading/></div>
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
                    ))) : (!error ? (
                        <BlankResult title={"Lawless lands"} info={"no laws have been passed yet"}/>
                        ) : (
                        <BlankResult title={"Server Error"} info={"No reply from the server"}/>
                        )
                    )}
                </div>
            </div>
        </div>
    );
};

export default Laws;