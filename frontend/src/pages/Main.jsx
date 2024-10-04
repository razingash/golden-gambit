import React from 'react';
import TopCompanies from "../components/UI/TopRating/TopCompanies";
import TopUsers from "../components/UI/TopRating/TopUsers";

const Main = () => {
    return (
        <div className={"section__main"}>
            <TopCompanies/>
            <TopUsers/>
        </div>
    );
};

export default Main;