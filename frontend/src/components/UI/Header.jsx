import React from 'react';

const Header = () => {
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
                        <a href="#" className="header__dropdown__item">
                            <svg className="svg__menu_icon">
                                <use xlinkHref="#icon_exit"></use>
                            </svg>
                            <div>log out</div>
                        </a>
                    </div>
                </div>
            </div>
            <div className={"header__items"}>
                <a href={"#"} className={"header__item"}>Stock</a>
                <a href={"#"} className={"header__item"}>Companies</a>
                <a href={"#"} className={"header__item"}>News</a>
                <a href={"#"} className={"header__item"}>Laws</a>
                <a href={"#"} className={"header__item"}>log out</a>
            </div>
        </div>
    );
};

export default Header;