import React, {useEffect, useState} from 'react';
import "../styles/company.css"
import {useParams} from "react-router-dom";
import {useFetching} from "../hooks/useFetching";
import CompaniesService from "../API/CompaniesService";
import AdaptiveLoading from "../components/UI/AdaptiveLoading";
import Chart from "../components/UI/Chart/Chart";
import BlankResult from "../components/UI/BlankResult/BlankResult";
import UpdateCompanyForm from "../components/UI/Forms/UpdateCompanyForm";
import {useAuth} from "../hooks/context/useAuth";
import CompanySharesList from "../components/UI/CompanySharesList/CompanySharesList";

const Company = () => {
    const {isAuth, tokenRef} = useAuth();
    const {ticker} = useParams();
    const [chartData, setChartData] = useState(null);
    const [companyData, setCompanyData] = useState(null);
    const [companyInventory, setInventory] = useState(null);
    const [fetchCompany, isCompanyLoading] = useFetching(async () => {
        return await CompaniesService.getCompany(ticker, tokenRef?.current?.access)
    })
    const [fetchChartData, isChartDataLoading] = useFetching(async () => {
        return await CompaniesService.getCompanyHistory(ticker)
    })
    const [fetchInventory, isInventoryLoading] = useFetching(async () => {
        return await CompaniesService.getCompanyInventory(ticker)
    })
    const [fetchProcure] = useFetching(async () => {
        return await CompaniesService.getCompanyNewProducts(ticker)
    }, 60000) // once per minute

    useEffect(() => {
        const loadData = async () => {
            const data = await fetchCompany();
            data && setCompanyData(data);
        }
        void loadData();
    }, [isCompanyLoading])

    useEffect(() => {
        const loadData = async () => {
            const data = await fetchChartData();
            data && setChartData(data.contents);
        }
        void loadData();
    }, [isChartDataLoading])

    useEffect(() => {
        const loadData = async () => {
            const data = await fetchInventory();
            data && setInventory(data);
        }
        isAuth && void loadData();
    }, [isInventoryLoading, isAuth])

    if (!companyData) {
        return <div className={"global__loading"}><AdaptiveLoading/></div>
    }

    return (
        <div className={"section__main"}>
            <div className={"field__company"}>
                <div className={"area__row"}>
                    <div className={"container__company"}>
                        <div className={"company__name"}>{companyData.name}</div>
                        <div className={"company__info"}>
                            <div className={"company__column"}>
                                <div className={"company__row"}>
                                    <div>ticker</div>
                                    <div>{companyData.ticker}</div>
                                </div>
                                <div className={"company__row"}>
                                    <div>type</div>
                                    <div>{companyData.type}</div>
                                </div>
                                <div className={"company__row"}>
                                    <div>dividendes percent</div>
                                    <div>{companyData.dividendes_percent}</div>
                                </div>
                                <div className={"company__row"}>
                                    <div>founding date</div>
                                    <div>{companyData.founding_date.split('T')[0]}</div>
                                </div>
                                <div className={"company__row"}>
                                    <div>preferred shares amount</div>
                                    <div>{companyData.preferred_shares_amount}</div>
                                </div>
                            </div>
                            <div className={"company__column"}>
                                <div className={"company__row"}>
                                    <div>company price</div>
                                    <div>{companyData.company_price}</div>
                                </div>
                                <div className={"company__row"}>
                                    <div>share price</div>
                                    <div>{companyData.share_price}</div>
                                </div>
                                <div className={"company__row"}>
                                    <div>silver reserve</div>
                                    <div>{companyData.silver_reserve}</div>
                                </div>
                                <div className={"company__row"}>
                                    <div>gold reserve</div>
                                    <div>{companyData.gold_reserve}</div>
                                </div>
                                <div className={"company__row"}>
                                    <div>shares amount</div>
                                    <div>{companyData.shares_amount}</div>
                                </div>
                            </div>
                        </div>
                    </div>
                    {companyData.isHead && (
                        <div className={"container__default"}>
                            <UpdateCompanyForm baseName={companyData.name} baseDividendes={companyData.dividendes_percent}/>
                        </div>
                    )}
                </div>
                <div className={"container__company_chart"}>
                    {companyData.isHead && (
                    <div className={"container__default field__company_products"}>
                        <div className={"button__submit"} onClick={fetchProcure}>procure</div>
                        <div className={"company__products_list"}>
                        {companyInventory && (companyInventory.map((product) => (
                            <div className={"company__products_item"} key={product.type}>
                                <div className={"cell__row"}>
                                    <div>type</div>
                                    <div>{product.type}</div>
                                </div>
                                <div className={"cell__row"}>
                                    <div>amount</div>
                                    <div>{product.amount}</div>
                                </div>
                                <div className={"cell__row"}>
                                    <div>maximum</div>
                                    <div>{product.max_amount}</div>
                                </div>
                            </div>
                        )))}
                        </div>
                    </div>
                    )}
                {chartData ? (chartData.length > 1 ? (
                        <Chart data={chartData} searchKey={'company_price'}/>
                    ) : (
                        <BlankResult title={"Not enough data to draw chart"} info={"This company hasn't made a sufficient contribution to the market economy yet"}/>
                    )
                ) : (
                    <AdaptiveLoading/>
                )}
                </div>
                <CompanySharesList ticker={ticker}/>
            </div>
        </div>
    );
};
export default Company;