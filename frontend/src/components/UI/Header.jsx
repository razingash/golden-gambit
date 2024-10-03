import {useAuth} from "../../hooks/context/useAuth";
import {Link} from "react-router-dom";

const Header = () => {
    const { isAuth, logout } = useAuth();
     //because of SPA need to use js to collapse the dropdown

    return (
        <div className={"section__header"}>
            <div className={"header__field"}>
                <input id="menu__toggle" type="checkbox"/>
                <label htmlFor="menu__toggle" className={"menu__button"}>
                    <span className={"toggle__bar"}></span>
                    <span className={"toggle__bar"}></span>
                    <span className={"toggle__bar"}></span>
                </label>
                <Link to={"/"} className={"header__sitename"}>Roumerchi</Link>
                <div className={"header__dropdown"}>
                    <div className="dropdown__field">
                        <label htmlFor="menu__toggle" className="dropdown__closing">
                            <div className={"cross"}></div>
                        </label>
                        <Link to={"/stock"} className="header__dropdown__item">
                            <svg className="svg__menu_icon">
                                <use xlinkHref="#icon_stock"></use>
                            </svg>
                            <div>Stock</div>
                        </Link>
                        <a href="#" className="header__dropdown__item">
                            <svg className="svg__menu_icon">
                                <use xlinkHref="#icon_town-council"></use>
                            </svg>
                            <div>Companies</div>
                        </a>
                        <Link to={"/news"} className="header__dropdown__item">
                            <svg className="svg__menu_icon">
                                <use xlinkHref="#icon_newspaper"></use>
                            </svg>
                            <div>News</div>
                        </Link>
                        <Link to={"/laws"} className="header__dropdown__item">
                            <svg className="svg__menu_icon">
                                <use xlinkHref="#icon_hammer"></use>
                            </svg>
                            <div>Laws</div>
                        </Link>
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
                <Link to={"/stock"} className={"header__item"}>Stock</Link>
                <div className={"header__stock_dropdown"}>
                    <Link to={"/stock/shares"} className={"header__item"}>Shares</Link>
                    <Link to={"/stock/products"} className={"header__item"}>Products</Link>
                </div>
                <a href={"#"} className={"header__item"}>Companies</a>
                <Link to={"/news"} className={"header__item"}>News</Link>
                <Link to={"/laws"} className={"header__item"}>Laws</Link>
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