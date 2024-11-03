import React, {useEffect, useState} from 'react';
import "../../styles/profile.css"
import "../../styles/company.css"
import {useFetching} from "../../hooks/useFetching";
import UserService from "../../API/UserService";
import BlankResult from "../../components/UI/BlankResult/BlankResult";
import {Link, Outlet} from "react-router-dom";
import NewCompanyForm from "../../components/UI/Forms/NewCompanyForm";

const Profile = () => {
    const [user, setUser] = useState(null);
    const [fetchUser, isUserLoading] = useFetching(async () => {
        return await UserService.getUserInfo();
    })

    useEffect(() => {
        const loadData = async () => {
            if (!isUserLoading && user === null) {
                const data = await fetchUser();
                data && setUser(data);
            }
        }
        void loadData();
    }, [isUserLoading])

    return (
        <div className={"section__main"}>
            <div className={"field__user_stats"}>
                {user ? (
                <div className={"area__row"}>
                    <div className={"container__default"}>
                        <div className={"container__header_1"}>{user.username}</div>
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
                    <NewCompanyForm/>
                </div>
                ) : (
                    <BlankResult title={"Error during loading user data"} info={"Most likely the error occurs due to a bad connection"} />
                )}
                <div className={"profile__header"}>
                    <Link to={"/profile/tickers/"} className={"profile__header__item"}>companies</Link>
                    <Link to={"/profile/shares/"} className={"profile__header__item"}>shares</Link>
                    <Link to={"/profile/recipes/"} className={"profile__header__item"}>recipes</Link>
                </div>
                <Outlet />
            </div>
        </div>
    );
};

export default Profile;