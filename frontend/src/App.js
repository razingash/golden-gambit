import "./styles/index.css";
import AppRouter from "./components/AppRouter";
import React from "react";
import {BrowserRouter} from "react-router-dom";
import Header from "./components/UI/Header";

function App() {
    return (
        <BrowserRouter>
            <Header/>
            <AppRouter/>
        </BrowserRouter>
    );
}

export default App;
