import React from 'react';
import "./blank_result.css"

const BlankResult = ({title, info}) => {
    return (
        <div className={"field__blank"}>
            <div className={"blank__title"}>{title}</div>
            <div className={"blank__info"}>{info}</div>
        </div>
    );
};

export default BlankResult;