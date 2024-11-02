import React, { useState, useEffect } from 'react';
import {useFetching} from "../../../hooks/useFetching";
import RatingService from "../../../API/RatingService";
import useWebSocket from "../../../hooks/useWebSocket";
import {calculateFluctuations, calculateWealth, formatNumber} from "../../../functions/utils";


const TopUsers = ({goldRate}) => {
    const [topUsers, setTopUsers] = useState([]);
    const [fetchTopUsers, isTopUsersLoading, fetchTopUsersError] = useFetching(async () => {
        return await RatingService.getTopUsers();
    });
    const [value] = useWebSocket('/top-players-wealth/');

    const updateUserWealth = (username, userSilver, userGold) => {
        setTopUsers(prevUsers =>
            prevUsers.map(user => {
                if (user.username === username) {
                    if (user.silver === userSilver && user.gold === userGold) {
                        return user; // crutch for Celery
                    }
                    let newPrice = +userSilver + userGold * goldRate
                    let oldPrice = +user.silver + user.gold * goldRate
                    const change = calculateFluctuations(newPrice, oldPrice);
                    return { ...user, silver: userSilver, gold: userGold, change: change };
                }
                return user;
            })
        );
    };

    useEffect(() => {
        const loadData = async () => {
            if (!isTopUsersLoading && Object.keys(topUsers).length === 0 && !fetchTopUsersError) {
                const data = await fetchTopUsers();
                data && setTopUsers(data);
            }
        };
        void loadData();
    }, [isTopUsersLoading]);

    useEffect(() => {
        if (value && value.username) {
            updateUserWealth(value.username, value.silver, value.gold);
        }
    }, [value]);

    return (
        <div className={"adaptive__field_1"}>
            <div className={"top_rating__list_2"}>
                <div className={"cell__simple top_rating_header"}>
                    <div className={"text_mod_username"}>username</div>
                    <div className={"text_mod_int"}>wealth</div>
                    <div className={"text_mod_int mod_hide"}>silver</div>
                    <div className={"text_mod_int mod_hide"}>gold</div>
                    <div className={"text_mod_fluctuations"}>changes</div>
                </div>
                {topUsers && !fetchTopUsersError ? topUsers.map((user) => (
                    <div className={"cell__simple"} key={user.username}>
                        <div className={"text_mod_username hover_backlight"}>{user.username}</div>
                        <div className={"text_mod_int hover_backlight"}>
                            {formatNumber(calculateWealth(user.silver, user.gold, goldRate))}
                        </div>
                        <div className={"text_mod_int hover_backlight mod_hide"}>{formatNumber(user.silver)}</div>
                        <div className={"text_mod_int hover_backlight mod_hide"}>{formatNumber(user.gold)}</div>
                        {user.change ? (user.change > 0 ? (
                            <div className={"text_mod_fluctuations state__positive"}>{user.change + "%"}</div>
                            ) : (
                            <div className={"text_mod_fluctuations state__negative"}>{user.change + "%"}</div>
                            )
                        ) : (
                            <div className={"text_mod_fluctuations state__default"}>0.00%</div>
                        )}
                    </div>
                )) : (
                    <div>No reply from the server</div>
                )}
            </div>
        </div>
    );
};

export default TopUsers;
