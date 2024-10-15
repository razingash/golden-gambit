import React, {useEffect, useState} from 'react';
import {useFetching} from "../hooks/useFetching";
import NewsService from "../API/NewsService";
import "../styles/laws_news.css"
import BlankResult from "../components/UI/BlankResult/BlankResult";

const News = () => {
    const [news, setNews] = useState([]);
    const [fetchNews, inNewsLoading] = useFetching(async () => {
        return await NewsService.getNewsList();
    })

    useEffect(() => {
        const loadData = async () => {
            if (!inNewsLoading && news.length === 0) {
                const news = await fetchNews();
                news && setNews(news);
            }
        }
        void loadData();
    }, [inNewsLoading])

    return (
        <div className={"section__main"}>
            <div className={"fields__news"}>
                <div className={"news__list"}>
                    {news.length > 0 ? (news.map((item) => (
                        <div>later continue</div>
                    ))) : (
                        <BlankResult title={"Switzerland be like"} info={"nothing significant has happened yet"}/>
                    )}
                </div>
            </div>
        </div>
    );
};

export default News;