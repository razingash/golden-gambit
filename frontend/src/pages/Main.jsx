import React from 'react';
import TopCompanies from "../components/UI/TopRating/TopCompanies";
import TopUsers from "../components/UI/TopRating/TopUsers";

const Main = () => {
    const formatNumber = (num) => {
        if (num >= 1e9) {
            return (num / 1e9).toFixed(1) + 'B';
        } else if (num >= 1e6) {
            return (num / 1e6).toFixed(1) + 'M';
        } else if (num >= 1e3) {
            return (num / 1e3).toFixed(1) + 'K';
        }
        return num.toString();
    }

    return (
        <div className={"section__main"}>
            <TopCompanies formatNumber={formatNumber}/>
            <TopUsers formatNumber={formatNumber}/>
        </div>
    );
};

export default Main;