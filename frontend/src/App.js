import "./styles/index.css";
import './styles/core.css'
import AppRouter from "./components/AppRouter";
import React from "react";
import {BrowserRouter} from "react-router-dom";
import Header from "./components/UI/Header";
import {AuthProvider} from "./hooks/context/useAuth";

function App() {
    return (
        <AuthProvider>
            <BrowserRouter>
                <Header/>
                <AppRouter/>
            </BrowserRouter>
        </AuthProvider>
    );
}

export default App;
