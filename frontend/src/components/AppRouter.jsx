import React from 'react';
import {Navigate, Route, Routes} from "react-router-dom";
import {publicRotes, unprivateRotes} from "../rotes/urls";

const AppRouter = () => {
    return (
        <Routes>
            {publicRotes.map(route =>
                <Route path={route.path} element={route.component} key={route.key}></Route>
            )}
            {unprivateRotes.map(route =>
                <Route path={route.path} element={route.component} key={route.key}></Route>
            )}
            <Route path="*" element={<Navigate to="" replace />} key={"redirect"}/>
        </Routes>
    );
};

export default AppRouter;