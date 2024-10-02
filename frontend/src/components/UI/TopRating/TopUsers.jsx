import React, {useEffect, useState} from 'react';
import {useFetching} from "../../../hooks/useFetching";
import RatingService from "../../../API/RatingService";

const TopUsers = ({formatNumber}) => {
    const [topUsers, setTopUsers] = useState([]);
    const [fetchTopUsers, isTopUsersLoading] = useFetching(async () => {
        return await RatingService.getTopUsers();
    })
    const columns = ["username", "wealth", "silver", "gold"]
    const formatColumns = ["wealth", "silver", "gold"]

    useEffect(() => {
        const loadData = async () => {
            const data = await fetchTopUsers();
            data && setTopUsers(data);
        }
        void loadData();
    }, [isTopUsersLoading])

    return (
        <div className={"field__top_rating"}>
            <div className={"top_rating__list"}>
                {columns.map((column) => (
                    <div className={"list__column"} key={column}>
                        <div className={"measurement_date"}></div>
                        {topUsers.length > 0 ? (topUsers.map((company) => (
                            <div className={"top_rating__column"} key={company}>
                                <div className={"top_rating__item"} key={company[column]}>
                                    {formatColumns.includes(column) ? formatNumber(company[column]): company[column]}
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

export default TopUsers;