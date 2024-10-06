import React, {useEffect, useRef, useState} from 'react';
import {useFetching} from "../../hooks/useFetching";
import UserService from "../../API/UserService";
import AdaptiveLoading from "../../components/UI/AdaptiveLoading";
import BlankResult from "../../components/UI/BlankResult/BlankResult";
import {useObserver} from "../../hooks/useObserver";
import {formatNumber, percentageOfNumber} from "../../functions/utils";
import {Link} from "react-router-dom";

const UserShares = () => {
    const [page, setPage] = useState(1);
    const [hasNext, setNext] = useState(false);
    const lastElement = useRef();
    const [shares, setShares] = useState([]);
    const [fetchUserShares, isUserSharesLoading] = useFetching(async () => {
        const data = await UserService.getUserShares(page);
        setShares((prevShares) => {
            const newShares = data.data.filter(
                (share) => !prevShares.some((obj) => obj.ticker === share.ticker)
            )
            return [...prevShares, ...newShares];
        })
        setNext(data.has_next)
    })

    useObserver(lastElement, fetchUserShares, isUserSharesLoading, hasNext, page, setPage);

    useEffect(() => {
        const loadData = async () => {
            await fetchUserShares();
        }
        void loadData();
    }, [page])

    if (isUserSharesLoading === true || isUserSharesLoading === null) {
        return <AdaptiveLoading/>
    }

    return (
        <div className={"profile__content__list"}>
            {shares.length > 0 ? (shares.map((company, index) => (
                <div className={"content__list__item"} key={company.ticker} ref={index === company.length - 1 ? lastElement : null}>
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
                        <div>{formatNumber(company.co_shares)}</div>
                    </div>
                    <div className={"content__row"}>
                        <div>preffered shares</div>
                        <div>{formatNumber(company.cp_shares)}</div>
                    </div>
                    <div className={"content_tug_of_war"}>
                        <div className={"tug_of_war_text"}>{percentageOfNumber(company.shares_amount, company.co_shares)}%</div>
                        <div className={"tug_of_war_bar"} style={{ width: `${percentageOfNumber(company.shares_amount, company.co_shares)}%` }} ></div>
                    </div>
                    <div className={"content_tug_of_war"}>
                        <div className={"tug_of_war_text"}>{percentageOfNumber(company.preferred_shares_amount, company.cp_shares)}%</div>
                        <div className={"tug_of_war_bar"} style={{ width: `${percentageOfNumber(company.shares_amount, company.co_shares)}%` }} ></div>
                    </div>
                </div>
            ))) : (
                <BlankResult title={"No shares found"} info={"You don't have any shares yet"}/>
            )}
        </div>
    );
};

export default UserShares;