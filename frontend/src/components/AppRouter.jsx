import React from 'react';
import {Navigate, Route, Routes} from "react-router-dom";
import {privateRotes, publicRotes, unprivateRotes} from "../rotes/urls";
import {useAuth} from "../hooks/context/useAuth";
import {useApiInterceptors} from "../hooks/useApiInterceptor";

const AppRouter = () => {
    useApiInterceptors();
    const {isAuth} = useAuth();

    return (
        <Routes>
            {isAuth ? (
                privateRotes.map(route =>
                    <Route path={route.path} element={route.component} key={route.key}>
                        {route.children && route.children.map(child => (
                            <Route path={child.path} element={child.component} key={child.key} />
                        ))}
                    </Route>
                )
            ) : (
                unprivateRotes.map(route =>
                    <Route path={route.path} element={route.component} key={route.key}></Route>
                )
            )}
            {publicRotes.map(route =>
                <Route path={route.path} element={route.component} key={route.key}></Route>
            )}
            <Route path="*" element={<Navigate to="" replace />} key={"redirect"}/>
        </Routes>
    );
};

export default AppRouter;