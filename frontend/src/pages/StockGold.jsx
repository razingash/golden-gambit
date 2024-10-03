import React, {useEffect, useState} from 'react';
import "../styles/stock.css"
import TradeGold from "../components/UI/TradeGold";
import Chart from "../components/UI/Chart/Chart";
import {useFetching} from "../hooks/useFetching";
import StockServices from "../API/StockServices";
import AdaptiveLoading from "../components/UI/AdaptiveLoading";

const StockGold = () => {
    const [chartData, setChartData] = useState(null);
    const [fetchGoldRateHistory, isGoldRateHistoryLoading] = useFetching(async () => {
        return await StockServices.getGoldRateHistory();
    })

    useEffect(() => {
        const loadData = async () => {
            const data = await fetchGoldRateHistory();
            data && setChartData(data.contents);
            data && console.log(data)
        }
        void loadData();
    }, [isGoldRateHistoryLoading])

    if(!chartData) {
        return <AdaptiveLoading/>
    }

    return (
        <div className={"section__main"}>
            <div className={"area__gold_trade"}>
                {chartData && chartData.length > 1 ? (
                    <Chart data={chartData} strokeStyle={0} backgroundStyle={0} pointerStyle={0} searchKey={'current price'}/>
                ) : (
                    <div>Loading...</div>
                )}
                <TradeGold/>
            </div>
        </div>
    );
};

export default StockGold;