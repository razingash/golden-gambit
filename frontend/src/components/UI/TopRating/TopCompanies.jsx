import React, {useEffect, useState} from 'react';
import "./top_rating.css"
import {useFetching} from "../../../hooks/useFetching";
import RatingService from "../../../API/RatingService";
import {formatNumber} from "../../../functions/utils";

const TopCompanies = () => {
    const [topCompanies, setTopCompanies] = useState([]);
    const [fetchTopCompanies, isTopCompaniesLoading] = useFetching(async () => {
        return await RatingService.getTopCompanies();
    })
    const columns = ["ticker", "name", "company_price", "dividendes_percent"]

    useEffect(() => {
        const loadData = async () => {
            const data = await fetchTopCompanies();
            data && setTopCompanies(data);
        }
        void loadData();
    }, [isTopCompaniesLoading])

    return (
        <div className={"field__top_rating"}>
            <div className={"top_rating__list"}>
                {columns.map((column) => (
                    <div className={"list__column"} key={column}>
                        <div className={"measurement_date"}></div>
                        {topCompanies.length > 0 ? (topCompanies.map((company) => (
                            <div className={"top_rating__column"} key={company}>
                                <div className={"top_rating__item"} key={company[column]}>
                                    {column === "company_price" ? formatNumber(company[column]): company[column]}
                                </div>
                            </div>
                        ))) : (
                            <div>Loading...</div>
                        )}
                    </div>
                ))}
            </div>
        </div>
    );
};

export default TopCompanies;