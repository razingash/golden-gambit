import {formatNumber, formatTimestamp} from "../../functions/utils";
import AdaptiveLoading from "./AdaptiveLoading";
import {AreaChart, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Area} from 'recharts';

const ChartSvg = ({ data, strokeStyle, backgroundStyle, pointerStyle, searchKey }) => {

    let key = '';
    searchKey && (key = searchKey);

    switch (strokeStyle) {
        case 0:  // for balance history
            strokeStyle = 'rgba(0,203,13, 1)';
            break
        case 1:
            strokeStyle = 'rgb(255,211,0)';
            break
        default:
            strokeStyle = 'rgb(0,146,255)';
            break
    }
    switch (backgroundStyle) {
        case 0:  // for balance history
            backgroundStyle = 'rgba(0,255,21,0.5)';
            break
        case 1:
            backgroundStyle = 'rgb(236,206,54)';
            break
        default:
            backgroundStyle = 'rgba(0,255,224,0.65)';
            break
    }
    switch (pointerStyle) {
        default:
            pointerStyle = '#f700ff';
            break
    }

    if (!data || data.length === 0) {
        return <AdaptiveLoading />;
    }

    return (
        <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={data} margin={{top: 20, right: 20, left: 0, bottom: 20}}>
                <defs>
                    <linearGradient id="chartGradient" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="0%" stopColor="rgba(26,31,25, 0.4)" />
                        <stop offset="100%" stopColor={backgroundStyle} />
                    </linearGradient>
                </defs>
                <CartesianGrid stroke="#444" strokeDasharray="3 3" vertical={false}/>
                <XAxis dataKey="timestamp" minTickGap={20} tick={{fill: "#aaa"}}
                       tickFormatter={(timestamp) => formatTimestamp(timestamp)}
                />
                <YAxis tick={{fill: "#aaa"}} tickFormatter={(tick) => formatNumber(tick.toFixed(2))}/>
                <Tooltip
                    labelFormatter={(timestamp) => formatTimestamp(timestamp)}
                    formatter={(value) => [formatNumber(value.toFixed(2)), key]}
                    contentStyle={{backgroundColor: "#333", color: "#fff", borderRadius: 5}}
                    itemStyle={{color: pointerStyle}}
                    cursor={{stroke: pointerStyle}}
                />
                <Area type="monotone" dataKey={searchKey} isAnimationActive={true} stroke={strokeStyle} fill="url(#chartGradient)" />
            </AreaChart>
        </ResponsiveContainer>
    );
};

export default ChartSvg;