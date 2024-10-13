import React, {useEffect, useRef, useState} from 'react';
import {useFetching} from "../../hooks/useFetching";
import UserService from "../../API/UserService";
import AdaptiveLoading from "../../components/UI/AdaptiveLoading";
import BlankResult from "../../components/UI/BlankResult/BlankResult";
import {useObserver} from "../../hooks/useObserver";
import {decodeCompanyType, decodeSharesType, formatNumber} from "../../functions/utils";
import {Link} from "react-router-dom";
import PrintNewSharesForm from "../../components/UI/Forms/PrintNewSharesForm";

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
        <div className={"area__row"}>
            {companies.length > 0 ? (companies.map((company, index) => (
                <div className={"container__default"} key={company.ticker} ref={index === companies.length - 1 ? lastElement : null}>
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
                        <div>ordinary shares</div>
                        <div>{formatNumber(company.co_shares)}</div>
                    </div>
                    <div className={"content__row"}>
                        <div>preferred shares</div>
                        <div>{formatNumber(company.cp_shares)}</div>
                    </div>
                    <PrintNewSharesForm ticker={company.ticker}/>
                </div>
            ))) : (
                <BlankResult title={"No tickers found"} info={"Apparently you have lost all your tickers or haven’t registered any..."}/>
            )}
        </div>
    );
};

export default UserCompanies;