import React, {useEffect, useRef, useState} from 'react';
import {useFetching} from "../../hooks/useFetching";
import UserService from "../../API/UserService";
import AdaptiveLoading from "../../components/UI/AdaptiveLoading";
import BlankResult from "../../components/UI/BlankResult/BlankResult";
import {useObserver} from "../../hooks/useObserver";

const UserCompanies = () => {
    const [page, setPage] = useState(1);
    const [hasNext, setNext] = useState(false);
    const lastElement = useRef();
    const [companies, setCompanies] = useState([]);
    const [fetchUserCompanies, isUserCompaniesLoading] = useFetching(async () => {
        const data = await UserService.getUserCompanies(page);
        setCompanies((prevCompanies) => {
            const newCompanies = data.data.filter(
                (company) => !prevCompanies.some((obj) => obj.ticker === company.ticker)
            )
            return [...prevCompanies, ...newCompanies]
        })
        setNext(data.has_next)
    })

    useObserver(lastElement, fetchUserCompanies, isUserCompaniesLoading, hasNext, page, setPage);

    useEffect(() => { // has_next
        const loadData = async () => {
            await fetchUserCompanies();
        }
        void loadData();
    }, [page])

    if(!companies) {
        return <AdaptiveLoading/>
    }

    return (
        <div className={"profile__content__list"}>
            {companies.length > 0 ? (companies.map((company) => (
                <div className={"content__list__item"} key={company.ticker}>
                    <div className={"content__header"}>{company.name}</div>
                </div>
            ))) : (
                <BlankResult title={"No companies found"} info={"Apparently you have lost all your companies or haven’t registered any..."}/>
            )}
        </div>
    );
};

export default UserCompanies;