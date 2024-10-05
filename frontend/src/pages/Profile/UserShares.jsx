import React, {useEffect, useRef, useState} from 'react';
import {useFetching} from "../../hooks/useFetching";
import UserService from "../../API/UserService";
import AdaptiveLoading from "../../components/UI/AdaptiveLoading";
import BlankResult from "../../components/UI/BlankResult/BlankResult";
import {useObserver} from "../../hooks/useObserver";

const UserShares = () => {
    const [page, setPage] = useState(1);
    const [hasNext, setNext] = useState(false);
    const lastElement = useRef();
    const [shares, setShares] = useState([]);
    const [fetchUserShares, isUserSharesLoading] = useFetching(async () => {
        const data = await UserService.getUserShares(page);
        setShares((prevShares) => {
            const newShares = data.data.filter(
                (share) => !prevShares.some((obj) => obj.ticker === share.ticker)
            )
            return [...prevShares, ...newShares];
        })
        setNext(data.has_next)
    })

    useObserver(lastElement, fetchUserShares, isUserSharesLoading, hasNext, page, setPage);

    useEffect(() => { //has_next
        const loadData = async () => {
            await fetchUserShares();
        }
        void loadData();
    }, [page])

    if (!shares) {
        return <AdaptiveLoading/>
    }

    return (
        <div className={"profile__content__list"}>
            {shares.length > 0 ? (shares.map((share) => (
                <div className={"content__list__item"} key={share.ticker}>
                    <div className={"content__header"}>{share.name}</div>
                </div>
            ))) : (
                <BlankResult title={"No shares found"} info={"You don't have any shares yet"}/>
            )}
        </div>
    );
};

export default UserShares;