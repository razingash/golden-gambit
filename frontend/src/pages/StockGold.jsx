import React, {useEffect, useState} from 'react';
import "../styles/stock.css"
import Chart from "../components/UI/Chart/Chart";
import {useFetching} from "../hooks/useFetching";
import StockServices from "../API/StockServices";
import AdaptiveLoading from "../components/UI/AdaptiveLoading";
import {useAuth} from "../hooks/context/useAuth";
import TradeGoldForm from "../components/UI/Forms/TradeGoldForm";

const StockGold = () => {
    const {isAuth} = useAuth();
    const [chartData, setChartData] = useState(null);
    const [fetchGoldRateHistory, isGoldRateHistoryLoading] = useFetching(async () => {
        return await StockServices.getGoldRateHistory();
    })

    useEffect(() => { // unused(useless): data.base_price, data.amount
        const loadData = async () => {
            const data = await fetchGoldRateHistory();
            data && setChartData(data.contents);
        }
        void loadData();
    }, [isGoldRateHistoryLoading])

    if(!chartData && isAuth === false) { // find better way
        return <div className={"global__loading"}><AdaptiveLoading/></div>
    }
    if (!chartData && isAuth === true) {
        return <AdaptiveLoading/>
    }

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
                    <TradeGoldForm/>
                    )}
                </div>
                {chartData.length > 1 ? (
                    <Chart data={chartData} strokeStyle={0} backgroundStyle={0} pointerStyle={0} searchKey={'current price'}/>
                ) : (
                    <div>Loading...</div>
                )}
            </div>
        </div>
    );
};

export default StockGold;