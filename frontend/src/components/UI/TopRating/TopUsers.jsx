import React, {useEffect, useState} from 'react';
import {useFetching} from "../../../hooks/useFetching";
import RatingService from "../../../API/RatingService";
import {formatNumber} from "../../../functions/utils";
import useWebSocket from "../../../hooks/useWebSocket";

const TopUsers = () => {
    const [topUsers, setTopUsers] = useState([]);
    const [fetchTopUsers, isTopUsersLoading] = useFetching(async () => {
        return await RatingService.getTopUsers();
    })
    const [messages, value, setValue, connected] = useWebSocket('ws/player-wealth/');

    const columns = ["username", "wealth", "silver", "gold"]
    const formatColumns = ["wealth", "silver", "gold"]

    useEffect(() => {
        const loadData = async () => {
            if (!isTopUsersLoading && topUsers.length === 0) {
                const data = await fetchTopUsers();
                data && setTopUsers(data);
            }
        }
        void loadData();
    }, [isTopUsersLoading])

    useEffect(() => {
        if (value) {
            console.log(value)
        }
    }, [value])

    return (
        <div className={"field__top_rating"}>
            <div className={"top_rating__list"}>
                {columns.map((column, index) => (
                    <div className={"list__column"} key={index}>
                        <div className={"measurement_date"}></div>
                        {topUsers.length > 0 ? (topUsers.map((company) => (
                            <div className={"top_rating__column"} key={company.ticker}>
                                <div className={"top_rating__item"}>
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