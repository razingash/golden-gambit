import {useFetching} from "../hooks/useFetching";
import CompaniesService from "../API/CompaniesService";
import {useEffect, useRef, useState} from "react";
import AdaptiveLoading from "../components/UI/AdaptiveLoading";
import BlankResult from "../components/UI/BlankResult/BlankResult";
import "../styles/companies.css"
import {Link} from "react-router-dom";
import {decodeCompanyType, formatNumber} from "../functions/utils";
import {useObserver} from "../hooks/useObserver";


const Companies = () => {
    const lastElement = useRef();
    const [page, setPage] = useState(1);
    const [hasNext, setNext] = useState(false);
    const [companies, setCompanies] = useState([]);
    const [fetchCompanies, isCompaniesLoading] = useFetching(async () => {
        const data = await CompaniesService.getCompaniesList(page);
        setCompanies((prevCompanies) => {
            const newCompanies = data.data.filter(
                (company) => !prevCompanies.some((obj) => obj.ticker === company.ticker)
            )
            return [...prevCompanies, ...newCompanies];
        })
        setNext(data.has_next)
    })

    useObserver(lastElement, fetchCompanies, isCompaniesLoading, hasNext, page, setPage);

    useEffect(() => {
        const loadData = async () => {
            await fetchCompanies();
        }
        void loadData();
    }, [page])

    if (!companies) {
        return <div className={"global__loading"}><AdaptiveLoading/></div>
    }

    return (
        <div className={"section__main"}>
            <div className={"field__companies"}>
                <div className={"companies__list"}>
                {companies.length > 0 ? companies.map((company, index) => (
                    <div className={"company__item"} key={company.ticker} ref={index === companies.length - 1 ? lastElement : null}>
                        <Link to={`/companies/${company.ticker}`} className={"company__name_s"}>{company.name}</Link>
                        <div className={"company__info_s"}>
                            <div className={"company__row_s"}>
                                <div>{decodeCompanyType(company.type)}</div>
                                <div>{company.ticker}</div>
                            </div>
                            <div className={"company__row_s"}>
                                <div>company price</div>
                                <div>{formatNumber(company.company_price)}</div>
                            </div>
                            <div className={"company__row_s"}>
                                <div>silver reserve</div>
                                <div>{formatNumber(company.silver_reserve)}</div>
                            </div>
                            <div className={"company__row_s"}>
                                <div>gold reserve</div>
                                <div>{formatNumber(company.gold_reserve)}</div>
                            </div>
                            <div className={"company__row_s"}>
                                <div>dividendes</div>
                                <div>{company.dividendes_percent} %</div>
                            </div>
                            <div className={"company__row_s"}>
                                <div>founding date</div>
                                <div>{company.founding_date.split('T')[0]}</div>
                            </div>
                        </div>
                    </div>
                )) : (
                    <BlankResult title={"Not enough data"} info={"No tickers have been registered yet"}/>
                )}
                </div>
            </div>
        </div>
    );
};

export default Companies;