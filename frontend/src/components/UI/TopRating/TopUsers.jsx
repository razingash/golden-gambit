import React, { useState, useEffect } from 'react';
import {useFetching} from "../../../hooks/useFetching";
import StockServices from "../../../API/StockServices";
import RatingService from "../../../API/RatingService";
import useWebSocket from "../../../hooks/useWebSocket";
import {calculateWealth, calculateWealthChanges, formatNumber} from "../../../functions/utils";


const TopUsers = () => {
    const [topUsers, setTopUsers] = useState({});
    const [fetchInitialGoldRate, isInitialGoldRateLoading] = useFetching(async () => {
        return await StockServices.getGoldSilverRate();
    });
    const [fetchTopUsers, isTopUsersLoading] = useFetching(async () => {
        return await RatingService.getTopUsers();
    });
    const [goldRate, setGoldRate] = useState(1000);
    const [messages, value, setValue, prevValue, setPrevValue, connected] = useWebSocket('/player-wealth/');

    useEffect(() => {
        const loadData = async () => {
            if (!isInitialGoldRateLoading) {
                const data = await fetchInitialGoldRate();
                if (data) setGoldRate(data.current_price);
            }
        };
        void loadData();
    }, [isInitialGoldRateLoading]);

    useEffect(() => {
        const loadData = async () => {
            if (!isTopUsersLoading && Object.keys(topUsers).length === 0) {
                const data = await fetchTopUsers();
                if (data) {
                    const usersObject = data.reduce((acc, user) => {
                        acc[user.username] = {
                            ...user,
                            prevSilver: user.silver,
                            prevGold: user.gold,
                        };
                        return acc;
                    }, {});
                    setTopUsers(usersObject);
                }
            }
        };
        void loadData();
    }, [isTopUsersLoading]);

    useEffect(() => {
        if (value) {
            setTopUsers((prevUsers) => {
                const updatedUser = prevUsers[value.username] || {};
                return {
                    ...prevUsers,
                    [value.username]: {
                        ...updatedUser,
                        silver: value.silver,
                        gold: value.gold,
                        prevSilver: updatedUser.silver,
                        prevGold: updatedUser.gold,
                    },
                };
            });
        }
    }, [value]);

    return (
        <div className={"adaptive__field_1"}>
            <div className={"top_rating__list_2"}>
                <div className={"cell__simple"}>
                    <div className={"text_mod_username"}>username</div>
                    <div className={"text_mod_int"}>wealth</div>
                    <div className={"text_mod_int mod_hide"}>silver</div>
                    <div className={"text_mod_int mod_hide"}>gold</div>
                    <div className={"text_mod_int"}>changes</div>
                </div>
                {Object.keys(topUsers).length > 0 ? (
                    Object.values(topUsers).map((user) => {
                        return (
                            <div className={"cell__simple"} key={user.username}>
                                <div className={"text_mod_username live_mod_hover_1"}>{user.username}</div>
                                <div className={"text_mod_int live_mod_hover_1"}>
                                    {formatNumber(calculateWealth(user.silver, user.gold, goldRate))}
                                </div>
                                <div className={"text_mod_int live_mod_hover_1 mod_hide"}>{formatNumber(user.silver)}</div>
                                <div className={"text_mod_int live_mod_hover_1 mod_hide"}>{formatNumber(user.gold)}</div>
                                <div className={"state__default text_mod_int"}>
                                    {user.prevSilver && user.prevGold ? (
                                        calculateWealthChanges(user, { silver: user.prevSilver, gold: user.prevGold }, goldRate)
                                    ) : ("0.00%")}
                                </div>
                            </div>
                        );
                    })
                ) : (
                    <div>Change Me</div>
                )}
            </div>
        </div>
    );
};

export default TopUsers;
