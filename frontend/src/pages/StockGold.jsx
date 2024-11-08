import React, {useEffect, useState} from 'react';
import "../styles/stock.css"
import {useFetching} from "../hooks/useFetching";
import StockServices from "../API/StockServices";
import AdaptiveLoading from "../components/UI/AdaptiveLoading";
import {useAuth} from "../hooks/context/useAuth";
import GlobalTradeGoldForm from "../components/UI/Forms/GlobalTradeGoldForm";
import UseEventSourcing from "../hooks/useEventSourcing";
import ChartSvg from "../components/UI/ChartSvg";
import BlankResult from "../components/UI/BlankResult/BlankResult";

const StockGold = () => {
    const {isAuth} = useAuth();
    const [isFormSpawned, setForm] = useState(false);
    const [chartData, setChartData] = useState(null);
    const [fetchInitialGoldRate, isInitialGoldRateLoading, goldRateError] = useFetching(async () => {
        return await StockServices.getGoldSilverRate();
    })
    const [fetchGoldRateHistory, isGoldRateHistoryLoading, goldRateHistoryError] = useFetching(async () => {
        return await StockServices.getGoldRateHistory();
    })
    const [highlightedElement, setHighlightedElement] = useState(null);
    const [value, setInitialValue] = UseEventSourcing('/stock/gold/', 'goldRate')
    const [prevValue, setPrevValue] = useState(null);

    const spawnForm = () => {
        setForm(!isFormSpawned);
    }

    useEffect(() => {
        const loadData = async () => {
            if (!isInitialGoldRateLoading && prevValue === null && !goldRateError) {
                const data = await fetchInitialGoldRate();
                data && setInitialValue(data)
            }
        }
        void loadData();
    }, [fetchInitialGoldRate, isInitialGoldRateLoading, goldRateError])

    useEffect(() => {
        if (value) {
            if (highlightedElement === null) {
                if (value?.current_price < prevValue) {
                    setHighlightedElement('dynamic_update_increase');
                }
                else if (value?.current_price > prevValue) {
                    setHighlightedElement('dynamic_update_decrease');
                }
                else if (value?.current_price === prevValue) {
                    setHighlightedElement('dynamic_update_static');
                }
            } else {
                setHighlightedElement(null);
            }
            setPrevValue(value?.current_price)
        }
    }, [value])

    useEffect(() => { // unused(useless for now): data.base_price, data.amount
        const loadData = async () => {
            if (!isGoldRateHistoryLoading && chartData === null && !goldRateHistoryError) {
                const data = await fetchGoldRateHistory();
                data && setChartData(data.contents);
            }
        }
        void loadData();
    }, [chartData, isGoldRateHistoryLoading, goldRateHistoryError])

    return (
        <div className={"section__main"}>
            <div className={"area__gold_trade"}>
                <div className={"field__gold_trade"}>
                    <div className={"cell__column"}>
                        <div className={"cell__row"}>
                            <div>current amount</div>
                            <div className={`${highlightedElement}`}>{value?.amount}</div>
                        </div>
                        <div className={"cell__row"}>
                            <div>current price</div>
                            <div className={`${highlightedElement}`}>{value?.current_price}</div>
                        </div>
                    </div>
                    {isAuth && (
                        <button className={"button__submit trade__gold__button"} onClick={spawnForm}>trade gold</button>
                    )}
                </div>
                {chartData ? chartData.length > 1 ? (
                    <div className="field__chart chart__gold">
                        <ChartSvg data={chartData} strokeStyle={1} backgroundStyle={1} pointerStyle={0} searchKey={'current price'}/>
                    </div>
                ) : (
                    <div className={"global__loading"}><AdaptiveLoading/></div>
                ) : (
                    <BlankResult title={"Server Error"} info={"No reply from the server"}/>
                )}
            </div>
            {isFormSpawned && <GlobalTradeGoldForm onClose={spawnForm}/>}
        </div>
    );
};

export default StockGold;