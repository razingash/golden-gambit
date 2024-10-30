import React, {useEffect, useState} from 'react';
import {useFetching} from "../hooks/useFetching";
import NewsService from "../API/NewsService";
import "../styles/laws_news.css"
import BlankResult from "../components/UI/BlankResult/BlankResult";
import {decodeEventState, decodeEventType} from "../functions/utils";
import AdaptiveLoading from "../components/UI/AdaptiveLoading";

const News = () => {
    const [news, setNews] = useState([]);
    const [fetchNews, inNewsLoading] = useFetching(async () => {
        return await NewsService.getNewsList();
    })

    useEffect(() => {
        const loadData = async () => {
            if (!inNewsLoading && news.length === 0) {
                const news = await fetchNews();
                news && setNews(news.data);
            }
        }
        void loadData();
    }, [inNewsLoading])

    if (inNewsLoading) {
        return <div className={"global__loading"}><AdaptiveLoading/></div>
    }
    if (!news) {
        return <BlankResult title={"Server Error 502"} info={"no response was received from the server"}/>
    }

    return (
        <div className={"section__main"}>
            <div className={"fields__news"}>
                <div className={"news__list"}>
                    {news.length > 0 ? (news.map((item) => (
                        <div className={"laws__item"} key={item.type}>
                            <div className={"law__title"}>{decodeEventType(item.type)}</div>
                            <div className={"law__description"}>{item.description}</div>
                            <div className={"law__limits"}>
                                <div>{decodeEventState(item.state)}</div>
                            </div>
                        </div>
                    ))) : (
                        <BlankResult title={"Switzerland be like"} info={"nothing significant has happened yet"}/>
                    )}
                </div>
            </div>
        </div>
    );
};

export default News;