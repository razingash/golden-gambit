import React, {useEffect, useState} from 'react';
import TopCompanies from "../components/UI/TopRating/TopCompanies";
import TopUsers from "../components/UI/TopRating/TopUsers";
import {useFetching} from "../hooks/useFetching";
import StockServices from "../API/StockServices";

const Main = () => {
    const [goldRate, setGoldRate] = useState(1000);
    const [fetchInitialGoldRate, isInitialGoldRateLoading] = useFetching(async () => {
        return await StockServices.getGoldSilverRate();
    });

    useEffect(() => {
        const loadData = async () => {
            if (!isInitialGoldRateLoading) {
                const data = await fetchInitialGoldRate();
                data && setGoldRate(data.current_price);
            }
        };
        void loadData();
    }, [isInitialGoldRateLoading]);

    return (
        <div className={"section__main"}>
            <TopCompanies />
            <TopUsers goldRate={goldRate}/>
        </div>
    );
};

export default Main;