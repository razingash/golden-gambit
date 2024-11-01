import React, {useEffect, useState} from 'react';
import "./top_rating.css"
import {useFetching} from "../../../hooks/useFetching";
import RatingService from "../../../API/RatingService";
import {calculateFluctuations, formatNumber} from "../../../functions/utils";
import useWebSocket from "../../../hooks/useWebSocket";
import {Link} from "react-router-dom";

const TopCompanies = () => {
    const [topCompanies, setTopCompanies] = useState([]);
    const [fetchTopCompanies, isTopCompaniesLoading] = useFetching(async () => {
        return await RatingService.getTopCompanies();
    })
    const [value] = useWebSocket('/top-companies-wealth/');

    const updateCompanyPriceAndChange = (ticker, newPrice) => {
        setTopCompanies(prevCompanies =>
            prevCompanies.map(company => {
                if (company.ticker === ticker) {
                    const change = calculateFluctuations(newPrice, company.daily_company_price);
                    return { ...company, company_price: newPrice, change: change };
                }
                return company;
            })
        );
    };

    useEffect(() => {
        const loadData = async () => {
            if (!isTopCompaniesLoading && topCompanies.length === 0) {
                const data = await fetchTopCompanies();
                data && setTopCompanies(data);
            }
        }
        void loadData();
    }, [isTopCompaniesLoading])

    useEffect(() => {
        if (value && value.ticker && value.company_price) {
            updateCompanyPriceAndChange(value.ticker, value.company_price);
        }
    }, [value]);

    return (
        <div className={"adaptive__field_1"}>
            <div className={"top_rating__list_2"}>
                <div className={"cell__simple top_rating_header"}>
                    <div className={"text_mod_username mod_hide"}>company</div>
                    <div className={"text_mod_int"}>ticker</div>
                    <div className={"text_mod_int mod_hide"}>dividendes</div>
                    <div className={"text_mod_int "}>price</div>
                    <div className={"text_mod_fluctuations"}>changes</div>
                </div>
                {topCompanies && topCompanies.map((company) => (
                    <div className={"cell__simple"} key={company.ticker}>
                        <Link to={`/companies/${company.ticker}`} className={"text_mod_username mod_hide hover_clickable_1"}>{company.name}</Link>
                        <Link to={`/companies/${company.ticker}`} className={"text_mod_int hover_clickable_1"}>{company.ticker}</Link>
                        <div className={"text_mod_int mod_hide hover_backlight"}>{company.dividendes_percent}%</div>
                        <div className={"text_mod_int hover_backlight"}>{formatNumber(company.company_price)}</div>
                        {company.change ? (company.change > 0 ? (
                            <div className={"text_mod_fluctuations state__positive"}>{company.change + "%"}</div>
                            ) : (
                            <div className={"text_mod_fluctuations state__negative"}>{company.change + "%"}</div>
                            )
                        ) : (
                            <div className={"text_mod_fluctuations state__default"}>0.00%</div>
                        )}
                    </div>
                ))}
            </div>
        </div>
    );
};

export default TopCompanies;