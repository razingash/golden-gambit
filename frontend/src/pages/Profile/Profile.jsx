import React, {useEffect, useState} from 'react';
import "../../styles/profile.css"
import {useFetching} from "../../hooks/useFetching";
import UserService from "../../API/UserService";
import BlankResult from "../../components/UI/BlankResult/BlankResult";
import {Link, Outlet} from "react-router-dom";

const Profile = () => {
    const [user, setUser] = useState(null);
    const [fetchUser, isUserLoading] = useFetching(async () => {
        return await UserService.getUserInfo();
    })

    useEffect(() => {
        const loadData = async () => {
            const data = await fetchUser();
            data && setUser(data);
        }
        void loadData();
    }, [isUserLoading])

    return (
        <div className={"section__main"}>
            <div className={"field__user_stats"}>
                <div className={"field__profile__info"}>
                {user ? (
                    <div className={"user__info"}>
                        <div className={"user__info__username"}>{user.username}</div>
                        <div className={"user__info__row"}>
                            <div>silver</div>
                            <div>{user.silver}</div>
                        </div>
                        <div className={"user__info__row"}>
                            <div>gold</div>
                            <div>{user.gold}</div>
                        </div>
                        <div className={"user__info__row"}>
                            <div>date joined</div>
                            <div>{user.date_joined.split('T')[0]}</div>
                        </div>
                    </div>
                ) : (
                    <BlankResult title={"Error during loading user data"} info={"Most likely the error occurs due to a bad connection"} />
                )}
                </div>
                <div className={"profile__header"}>
                    <Link to={"/profile/companies/"} className={"profile__header__item"}>companies</Link>
                    <Link to={"/profile/shares/"} className={"profile__header__item"}>shares</Link>
                    <Link to={"/profile/recipes/"} className={"profile__header__item"}>recipes</Link>
                </div>
                <div className={"field__profile__content"}>
                    <Outlet />
                </div>
            </div>
        </div>
    );
};

export default Profile;