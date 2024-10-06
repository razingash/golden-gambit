import React, {useEffect, useRef, useState} from 'react';
import {useFetching} from "../../hooks/useFetching";
import UserService from "../../API/UserService";
import AdaptiveLoading from "../../components/UI/AdaptiveLoading";
import BlankResult from "../../components/UI/BlankResult/BlankResult";
import {useObserver} from "../../hooks/useObserver";
import {formatNumber} from "../../functions/utils";
import {Link} from "react-router-dom";

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

    useEffect(() => {
        const loadData = async () => {
            await fetchUserCompanies();
        }
        void loadData();
    }, [page])

    if(isUserCompaniesLoading === true || isUserCompaniesLoading === null) {
        return <AdaptiveLoading/>
    }

    return (
        <div className={"profile__content__list"}>
            {companies.length > 0 ? (companies.map((company, index) => (
                <div className={"content__list__item"} key={company.ticker} ref={index === companies.length - 1 ? lastElement : null}>
                    <Link to={`/companies/${company.ticker}`} className={"content__header"}>{company.name}</Link>
                    <div className={"content__row"}>
                        {company.isFounder && <div className={"content__s"}>Founder</div>}
                        {company.isHead && <div className={"content__s"}>Owner</div>}
                    </div>
                    <div className={"content__row"}>
                        <div>{company.type}</div>
                        <div>{company.ticker}</div>
                    </div>
                    <div className={"content__row"}>
                        <div>company price</div>
                        <div>{formatNumber(company.price)}</div>
                    </div>
                    <div className={"content__row"}>
                        <div>ordinary shares</div>
                        <div>{formatNumber(company.shares_amount)}</div>
                    </div>
                    <div className={"content__row"}>
                        <div>preffered shares</div>
                        <div>{formatNumber(company.preferred_shares_amount)}</div>
                    </div>
                </div>
            ))) : (
                <BlankResult title={"No companies found"} info={"Apparently you have lost all your companies or haven’t registered any..."}/>
            )}
        </div>
    );
};

export default UserCompanies;