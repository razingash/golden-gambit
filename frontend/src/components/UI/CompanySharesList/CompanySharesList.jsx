import React, {useEffect, useRef, useState} from 'react';
import {useAuth} from "../../../hooks/context/useAuth";
import {useFetching} from "../../../hooks/useFetching";
import StockServices from "../../../API/StockServices";
import {useObserver} from "../../../hooks/useObserver";
import AdaptiveLoading from "../AdaptiveLoading";
import BlankResult from "../BlankResult/BlankResult";
import GlobalBuyCurrentCompanyShares from "../Forms/GlobalBuyCurrentCompanyShares";
import {decodeSharesType} from "../../../functions/utils";

const CompanySharesList = ({ticker}) => {
    const {isAuth, tokenRef} = useAuth();
    const [page, setPage] = useState(1);
    const [hasNext, setNext] = useState(false);
    const lastElement = useRef();
    const [shares, setShares] = useState([]);
    const [selectedShares, setSelectedShares] = useState(null);
    const [isFormSpawned, setForm] = useState(false);

    const [fetchCompanyShares, isCompanySharesLoading, fetchCompanySharesError] = useFetching(async () => {
        const data = await StockServices.getCompanySharesOnSale(page, ticker, tokenRef?.current?.access);
        setShares((prevShares) => {
            const newShares = data.data.filter(
                (share) => !prevShares.some((obj) => obj.id === share.id)
            )
            return [...prevShares, ...newShares]
        })
        setNext(data.has_next)
    })

    useObserver(lastElement, fetchCompanyShares, isCompanySharesLoading, hasNext, page, setPage);

    useEffect(() => {
        const loadData = async () => {
            await fetchCompanyShares();
        }
        void loadData();
    }, [page])

    const spawnForm = (company) => {
        setSelectedShares(company);
        setForm(true);
    }
    const closeForm = () => {
        setForm(false);
    }

    if(isCompanySharesLoading === true || isCompanySharesLoading === null) {
        return <AdaptiveLoading/>
    }

    return (
        <div className={"field__shares"}>
            {shares.length > 0 ? (
                <div className={"shares__list"}>
                    {shares.map((share, index) => (
                        <div className={"share__item"} key={share.id} ref={index === shares.length - 1 ? lastElement : null}>
                            <div className={"share__title"}>{share.name}</div>
                            <div className={"share__row"}>
                                <div>ticker</div>
                                <div>{share.ticker}</div>
                            </div>
                            <div className={"share__row"}>
                                <div>amount</div>
                                <div>{share.amount}</div>
                            </div>
                            <div className={"share__row"}>
                                <div>price</div>
                                <div>{share.price}</div>
                            </div>
                            <div className={"share__row"}>
                                <div>type</div>
                                <div>{decodeSharesType(share.shares_type)}</div>
                            </div>
                            {isAuth ? (
                                <button className={"button__submit"} onClick={() => spawnForm(share)}>buy</button>
                        ) : (
                            <div className={"lon_in_wish_container"}>
                                <div className={"log_in_wish"}>Sign In!</div>
                            </div>
                        )}
                        </div>
                    ))}
                </div>
            ) : !fetchCompanySharesError ? (
                <BlankResult title={"No lots found for sale"} info={"Company's shares aren't currently for sale"}/>
            ): (
                <BlankResult title={"Server Error"} info={"No reply from the server"}/>
            )}
            {isFormSpawned && <GlobalBuyCurrentCompanyShares shares={selectedShares} onClose={closeForm} setShares={setShares}/>}
        </div>
    );
};

export default CompanySharesList;