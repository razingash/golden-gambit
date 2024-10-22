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
    const [messages, value, setValue, connected] = useWebSocket('/player-wealth/');

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
            setTopUsers((prevUsers) => {
                return prevUsers.map(user => {
                    if (user.username === value.username) {
                        return {...user, silver: value.silver, gold: value.gold}
                    }
                    return user;
                });
            });
        }
    }, [value]);
    //объединить два топа чтобы сделать общее колесо загрузки?
    //изменить хук, возможно сделать два, или отдельный компонент под каждый случай(на аутсайдычах)
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
                {topUsers.length > 0 ? (topUsers.map((user) => (
                    <div className={"cell__simple"} key={user.username}>
                        <div className={"text_mod_username live_mod_hover_1"}>{user.username}</div>
                        <div className={"text_mod_int live_mod_hover_1"}>{formatNumber(user.wealth)}</div>
                        <div className={"text_mod_int live_mod_hover_1 mod_hide"}>{formatNumber(user.silver)}</div>
                        <div className={"text_mod_int live_mod_hover_1 mod_hide"}>{formatNumber(user.gold)}</div>
                        <div className={"state__default text_mod_int"}>00.00%</div>
                    </div>
                ))) : (
                    <div>Change Me</div>
                )}
            </div>
        </div>
    );
};

export default TopUsers;