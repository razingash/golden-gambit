import React from 'react';
import {useAuth} from "../../hooks/context/useAuth";
import {Link} from "react-router-dom";

const Header = () => {
    const { isAuth, logout } = useAuth();

    return (
        <div className={"header__section"}>
            <div className={"header__field"}>
                <input id="menu__toggle" type="checkbox"/>
                <label htmlFor="menu__toggle" className={"menu__button"}>
                    <span className={"toggle__bar"}></span>
                    <span className={"toggle__bar"}></span>
                    <span className={"toggle__bar"}></span>
                </label>
                <div className={"header__sitename"}>Roumerchi</div>
                <div className={"header__dropdown"}>
                    <div className="dropdown__field">
                        <label htmlFor="menu__toggle" className="dropdown__closing">
                            <div className={"cross"}></div>
                        </label>
                        <a href="#" className="header__dropdown__item">
                            <svg className="svg__menu_icon">
                                <use xlinkHref="#icon_stock"></use>
                            </svg>
                            <div>Stock</div>
                        </a>
                        <a href="#" className="header__dropdown__item">
                            <svg className="svg__menu_icon">
                                <use xlinkHref="#icon_town-council"></use>
                            </svg>
                            <div>Companies</div>
                        </a>
                        <a href="#" className="header__dropdown__item">
                            <svg className="svg__menu_icon">
                                <use xlinkHref="#icon_newspaper"></use>
                            </svg>
                            <div>News</div>
                        </a>
                        <a href="#" className="header__dropdown__item">
                            <svg className="svg__menu_icon">
                                <use xlinkHref="#icon_hammer"></use>
                            </svg>
                            <div>Laws</div>
                        </a>
                        {isAuth ? (
                            <div onClick={async () => await logout()} className="header__dropdown__item">
                                <svg className="svg__menu_icon">
                                    <use xlinkHref="#icon_exit"></use>
                                </svg>
                                <div>log out</div>
                            </div>
                        ) : (
                            <Link to={"/authentication"} className="header__dropdown__item">
                                <svg className="svg__menu_icon">
                                    <use xlinkHref="#icon_login"></use>
                                </svg>
                                <div>log in</div>
                            </Link>
                        )}
                    </div>
                </div>
            </div>
            <div className={"header__items"}>
                <a href={"#"} className={"header__item"}>Stock</a>
                <a href={"#"} className={"header__item"}>Companies</a>
                <a href={"#"} className={"header__item"}>News</a>
                <a href={"#"} className={"header__item"}>Laws</a>
                {isAuth ? (
                    <div onClick={async () => await logout()} className={"header__item"}>log out</div>
                ) : (
                    <Link to={"/authentication"} className={"header__item"}>log in</Link>
                )}
            </div>
        </div>
    );
};

export default Header;