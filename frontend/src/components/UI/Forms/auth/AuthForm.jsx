import useInput from "../../../../hooks/useInput";
import "./auth.css"
import {useCallback, useEffect, useState} from "react";
import {useAuth} from "../../../../hooks/context/useAuth";

const AuthForm = () => {
    const username = useInput('');
    const password= useInput('');
    const [canSubmit, setCanSubmit] = useState(true);
    const [isNewbie, setIsNewbie] = useState(false);
    const [activeElement, setActiveElement] = useState(null);
    const { login, register, loginError, registerError } = useAuth();

    const registerUser = async (e) => {
        e.preventDefault();
        if (!canSubmit) return;

        setCanSubmit(false);
        await register(username.value, password.value)

        setTimeout(() => {
            setCanSubmit(true);
        }, 1000)
    }

    const loginUser = async (e) => {
        e.preventDefault();
        if (!canSubmit) return;

        setCanSubmit(false);
        await login(username.value, password.value);

        setTimeout(() => {
            setCanSubmit(true);
        }, 1000)
    }

    const handleSignUpClick = useCallback((event) => {
        setIsNewbie(true);
        setActiveElement(event.target);
    }, [])

    const handleSignInClick = useCallback((event) => {
        setIsNewbie(false);
        setActiveElement(event.target);
    }, [])

    useEffect(() => {
        setActiveElement(document.querySelector('.conductor__item:first-child'));
    }, [])
    registerError && console.log(registerError.username)

    return (
        <div className={"field__authentication"}>
            <div className={"authentication__conductor"}>
                <div className={`conductor__item ${activeElement?.innerText === 'Sign in' ? 'active' : ''}`} onClick={handleSignInClick}>
                    Sign in
                </div>
                <div className={`conductor__item ${activeElement?.innerText === 'Sign up' ? 'active' : ''}`} onClick={handleSignUpClick}>
                    Sign up
                </div>
            </div>
            {isNewbie ? (
            <form onSubmit={registerUser} className={"form__auth"}>
                <div className={"field__input"}>
                    <input className={"input__login"} {...username} type={"text"} placeholder={"username..."}/>
                    <svg className={"svg__auth-help"} viewBox="0 0 20 20">
                        <g transform="matrix(1.128 0 0 1.128 -1.284 -.8425)"><circle cx="10" cy="4.497" r="3.75"/><path d="M3.546 18.14c-1.302-.669-1.746-1.65-1.742-3.853.002-1.117.169-2.607.372-3.312.632-2.196 2.846-3.937 3.965-3.117 2.455 1.798 5.192 1.795 7.723-.008.638-.454 1.82-.04 2.776.974 1.022 1.084 1.541 2.95 1.555 5.596.008 1.523-.099 2.046-.544 2.646-.986 1.33-1.379 1.402-7.647 1.402-4.1 0-6.009-.097-6.457-.327z"/></g>
                    </svg>
                </div>
                {registerError?.username && <div className={"cell__error"}>{registerError?.username}</div>}
                <div className={"field__input"}>
                    <input className={"input__password"} {...password} type={"password"} placeholder={"password..."}/>
                    <svg className="svg__auth-help" viewBox="0 0 20 20">
                        <path d="M10.07 0a6.1 6.1 0 0 0-6.1 6.1v2.035H2.348c-.705 0-1.276.571-1.276 1.276v9.313c0 .704.571 1.276 1.276 1.276h15.3c.704 0 1.276-.571 1.276-1.276V9.411c0-.705-.571-1.276-1.276-1.276h-1.622V6.1a6.03 6.03 0 0 0-5.96-6.1zm-.014 2.634a3.47 3.47 0 0 1 3.412 3.525v1.977H6.531V6.159c0-1.947 1.578-3.525 3.525-3.525z"/>
                    </svg>
                </div>
                {registerError?.password && <div className={"cell__error"}>{registerError?.password}</div>}
                <button className={"button__submit"}>Register</button>
            </form>
            ) : (
            <form onSubmit={loginUser} className={"form__auth"}>
                <div className={"field__input"}>
                    <input className={"input__login"} {...username} type={"text"} placeholder={"username..."}/>
                    <svg className="svg__auth-help">
                        <use xlinkHref="#icon_user"></use>
                    </svg>
                </div>
                <div className={"field__input"}>
                    <input className={"input__password"} {...password} type={"password"} placeholder={"password..."}/>
                    <svg className={"svg__auth-help"} viewBox="0 0 20 20">
                        <path d="M10.07 0a6.1 6.1 0 0 0-6.1 6.1v2.035H2.348c-.705 0-1.276.571-1.276 1.276v9.313c0 .704.571 1.276 1.276 1.276h15.3c.704 0 1.276-.571 1.276-1.276V9.411c0-.705-.571-1.276-1.276-1.276h-1.622V6.1a6.03 6.03 0 0 0-5.96-6.1zm-.014 2.634a3.47 3.47 0 0 1 3.412 3.525v1.977H6.531V6.159c0-1.947 1.578-3.525 3.525-3.525z"/>
                    </svg>
                </div>
                {loginError && <div className={"cell__error"}>{loginError?.detail}</div>}
                <button className={"button__submit"}>log in</button>
            </form>
            )}
        </div>
    );
};

export default AuthForm;