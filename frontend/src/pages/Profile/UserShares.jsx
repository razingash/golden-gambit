import React, {useEffect, useRef, useState} from 'react';
import {useFetching} from "../../hooks/useFetching";
import UserService from "../../API/UserService";
import AdaptiveLoading from "../../components/UI/AdaptiveLoading";
import BlankResult from "../../components/UI/BlankResult/BlankResult";
import {useObserver} from "../../hooks/useObserver";
import {decodeCompanyType, formatNumber} from "../../functions/utils";
import {Link} from "react-router-dom";
import GlobalSellSharesForm from "../../components/UI/Forms/GlobalSellSharesForm";

const UserShares = () => {
    const [page, setPage] = useState(1);
    const [hasNext, setNext] = useState(false);
    const lastElement = useRef();
    const [shares, setShares] = useState([]);
    const [selectedTicker, setSelectedTicker] = useState(null);
    const [isFormSpawned, setForm] = useState(false);

    const [fetchUserShares, isUserSharesLoading, fetchUserSharesError] = useFetching(async () => {
        const data = await UserService.getUserShares(page);
        setShares((prevShares) => {
            const newShares = data.data.filter(
                (share) => !prevShares.some((obj) => obj.ticker === share.ticker)
            )
            return [...prevShares, ...newShares];
        })
        setNext(data.has_next)
    })

    const spawnForm = (company) => {
        setSelectedTicker(company);
        setForm(true);
    }
    const closeForm = () => {
        setForm(false);
    }


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
        <div className={"area__row"}>
            {isUserSharesLoading === true || isUserSharesLoading === null ? (
                <AdaptiveLoading />
            ) : shares.length > 0 ? (shares.map((company, index) => (
                <div className={"container__default pie_chart_container"} key={company.ticker} ref={index === company.length - 1 ? lastElement : null}>
                    <Link to={`/companies/${company.ticker}`} className={"container__header_1 content__header"}>{company.name}</Link>
                    <div className={"content__row"}>
                        {company.isFounder && <div className={"content__s"}>Founder</div>}
                        {company.isHead && <div className={"content__s"}>Owner</div>}
                    </div>
                    <div className={"content__row"}>
                        <div>{decodeCompanyType(company.type)}</div>
                        <div>{company.ticker}</div>
                    </div>
                    <div className={"content__row"}>
                        <div>company price</div>
                        <div>{formatNumber(company.price)}</div>
                    </div>
                    <div className={"content__row"}>
                        <div>company ordinary shares</div>
                        <div>{formatNumber(company.co_shares)}</div>
                    </div>
                    <div className={"content__row"}>
                        <div>company preferred shares</div>
                        <div>{formatNumber(company.cp_shares)}</div>
                    </div>
                    <div className={"content__row"}>
                        <div>ordinary shares</div>
                        <div>{formatNumber(company.shares_amount)}</div>
                    </div>
                    <div className={"content__row"}>
                        <div>preferred shares</div>
                        <div>{formatNumber(company.preferred_shares_amount)}</div>
                    </div>
                    <button className={"button__submit"} onClick={() => spawnForm(company.ticker)}>sell</button>
                </div>
            ))) : (!fetchUserSharesError ? (
                <BlankResult title={"No shares found"} info={"You don't have any shares yet"}/>
                ) : (
                <BlankResult title={"Server Error"} info={"No reply from the server"}/>
                )
            )}
            {isFormSpawned && <GlobalSellSharesForm ticker={selectedTicker} setShares={setShares} onClose={closeForm}/>}
        </div>
    );
};

export default UserShares;