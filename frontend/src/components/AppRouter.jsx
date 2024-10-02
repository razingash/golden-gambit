import React from 'react';
import {Navigate, Route, Routes} from "react-router-dom";
import {privateRotes, publicRotes, unprivateRotes} from "../rotes/urls";
import {useAuth} from "../hooks/context/useAuth";

const AppRouter = () => {
    const {isAuth} = useAuth();

    return (
        <Routes>
            {isAuth && (
                <>
                {privateRotes.map(route =>
                    <Route path={route.path} element={route.component} key={route.key}></Route>
                )}
                </>
            )}
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