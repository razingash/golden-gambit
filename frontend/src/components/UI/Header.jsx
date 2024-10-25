import {useAuth} from "../../hooks/context/useAuth";
import {Link} from "react-router-dom";

const Header = () => {
    const { isAuth, logout } = useAuth();
     //because of SPA need to use js to collapse the dropdown
    const closeMenu = () => { // and even trick with label doesn't work
        const checkbox = document.getElementById("menu__toggle");
        document.body.style.overflow = '';
        checkbox.checked = false;
    };

    return (
        <>
        <div className={"section__header"}>
            <div className={"header__field"}>
                <input id="menu__toggle" onChange={(e) => (document.body.style.overflow = e.target.checked ? 'hidden' : 'auto')} type="checkbox"/>
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
                        {isAuth && (
                            <Link to={"/profile"} className="header__dropdown__item" onClick={closeMenu}>
                                <svg className="svg__menu_icon">
                                    <use xlinkHref="#icon_user"></use>
                                </svg>
                                <div>Profile</div>
                            </Link>
                        )}
                        <div className={"header__dropdown__mini"}>
                            <Link to={"/stock"} className="header__dropdown__item" onClick={closeMenu}>
                                <svg className="svg__menu_icon">
                                    <use xlinkHref="#icon_stock"></use>
                                </svg>
                                <div>Stock</div>
                            </Link>
                            <Link to={"/stock/shares"} className={"header__dropdown__item_mini"} onClick={closeMenu}>
                                Shares
                            </Link>
                            <Link to={"/stock/products"} className={"header__dropdown__item_mini"} onClick={closeMenu}>
                                Products
                            </Link>
                        </div>
                        <Link to={"/companies"} className="header__dropdown__item" onClick={closeMenu}>
                            <svg className="svg__menu_icon">
                                <use xlinkHref="#icon_town-council"></use>
                            </svg>
                            <div>Companies</div>
                        </Link>
                        <Link to={"/news"} className="header__dropdown__item" onClick={closeMenu}>
                            <svg className="svg__menu_icon">
                                <use xlinkHref="#icon_newspaper"></use>
                            </svg>
                            <div>News</div>
                        </Link>
                        <Link to={"/laws"} className="header__dropdown__item" onClick={closeMenu}>
                            <svg className="svg__menu_icon">
                                <use xlinkHref="#icon_hammer"></use>
                            </svg>
                            <div>Laws</div>
                        </Link>
                        {isAuth ? (
                            <div onClick={async () => await logout()} className="header__dropdown__item" >
                                <svg className="svg__menu_icon">
                                    <use xlinkHref="#icon_exit"></use>
                                </svg>
                                <div>log out</div>
                            </div>
                        ) : (
                            <Link to={"/authentication"} className="header__dropdown__item" onClick={closeMenu}>
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
                <div className={"header__item"}>
                    <Link className={"header__stock header__item"} to={"/stock"}>Stock</Link>
                    <div className={"header__stock_dropdown"}>
                        <span className={"dropdown__line"}></span>
                        <Link to={"/stock/shares"} className={"header__item"}>Shares</Link>
                        <Link to={"/stock/products"} className={"header__item"}>Products</Link>
                    </div>
                </div>
                {isAuth && <Link to={"/profile"} className={"header__item"}>Profile</Link>}
                <Link to={"/companies"} className={"header__item"}>Companies</Link>
                <Link to={"/news"} className={"header__item"}>News</Link>
                <Link to={"/laws"} className={"header__item"} >Laws</Link>
                {isAuth ? (
                    <div onClick={async () => await logout()} className={"header__item"}>log out</div>
                ) : (
                    <Link to={"/authentication"} className={"header__item"}>log in</Link>
                )}
            </div>
        </div>
        <div className={"pillar__container pillar__container_left"}>
            <svg className={"svg__pillar svg__pillar_top"}>
                <use xlinkHref="#flexible_pillar_tip"></use>
            </svg>
            <svg className={"svg__pillar svg__pillar_center"}>
                <use xlinkHref="#flexible_pillar_center"></use>
            </svg>
            <svg className={"svg__pillar svg__pillar_bottom"}>
                <use xlinkHref="#flexible_pillar_tip"></use>
            </svg>
        </div>
        <div className={"pillar__container pillar__container_right"}>
            <svg className={"svg__pillar svg__pillar_top"}>
                <use xlinkHref="#flexible_pillar_tip"></use>
            </svg>
            <svg className={"svg__pillar svg__pillar_center"}>
                <use xlinkHref="#flexible_pillar_center"></use>
            </svg>
            <svg className={"svg__pillar svg__pillar_bottom"}>
                <use xlinkHref="#flexible_pillar_tip"></use>
            </svg>
        </div>
        </>
    );
};

export default Header;