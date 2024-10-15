import React, {useEffect, useState} from 'react';
import "../styles/stock.css"
import Chart from "../components/UI/Chart/Chart";
import {useFetching} from "../hooks/useFetching";
import StockServices from "../API/StockServices";
import AdaptiveLoading from "../components/UI/AdaptiveLoading";
import {useAuth} from "../hooks/context/useAuth";
import GlobalTradeGoldForm from "../components/UI/Forms/GlobalTradeGoldForm";

const StockGold = () => {
    const {isAuth} = useAuth();
    const [isFormSpawned, setForm] = useState(false);
    const [chartData, setChartData] = useState(null);
    const [fetchGoldRateHistory, isGoldRateHistoryLoading] = useFetching(async () => {
        return await StockServices.getGoldRateHistory();
    })

    const spawnForm = () => {
        setForm(!isFormSpawned);
    }

    useEffect(() => { // unused(useless for now): data.base_price, data.amount
        const loadData = async () => {
            if (!isGoldRateHistoryLoading && chartData === null) {
                const data = await fetchGoldRateHistory();
                data && setChartData(data.contents);
            }
        }
        void loadData();
    }, [isGoldRateHistoryLoading])

    return (
        <div className={"section__main"}>
            <div className={"area__gold_trade"}>
                <div className={"field__gold_trade"}>
                    <div className={"cell__column"}>
                        <div className={"cell__row"}>
                            <div>current amount</div>
                            <div>redo with hook</div>
                        </div>
                        <div className={"cell__row"}>
                            <div>current price</div>
                            <div>redo with hook</div>
                        </div>
                    </div>
                    {isAuth && (
                        <button className={"button__submit trade__gold__button"} onClick={spawnForm}>trade gold</button>
                    )}
                </div>
                {chartData && chartData.length > 1 ? (
                    <Chart data={chartData} strokeStyle={0} backgroundStyle={0} pointerStyle={0} searchKey={'current price'}/>
                ) : (
                    <div className={"global__loading"}><AdaptiveLoading/></div>
                )}
            </div>
            {isFormSpawned && <GlobalTradeGoldForm onClose={spawnForm}/>}
        </div>
    );
};

export default StockGold;