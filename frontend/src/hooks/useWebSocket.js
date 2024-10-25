import React, {useEffect, useRef, useState} from 'react';
import {websocketBaseURL} from "./useApiInterceptor";

const UseWebSocket = (link) => {
    // лучше всего будет сделать два хука - для графиков с messages и обычный с прошлым состоянием
    const [messages, setMessages] = useState([]);
    const [prevValue, setPrevValue] = useState(null);
    const [value, setValue] = useState(null);
    const [connected, setConnected] = useState(false);
    const socketRef = useRef();

    useEffect(() => {
        socketRef.current = new WebSocket(`${websocketBaseURL}${link}`); // ws://localhost:8000/ws

        socketRef.current.onopen = () => {
            console.log('connected')
            setConnected(true);

        }

        socketRef.current.onmessage = (event) => {
            const message = JSON.parse(event.data);
            console.log(message)
            if (JSON.stringify(message) !== JSON.stringify(prevValue)) {
                setMessages(prev => [message, ...prev]);
                setPrevValue(message);
                setValue(message);
            }
        }

        socketRef.current.onclose = () => {
            console.log('closing')
        }

        socketRef.current.onerror = () => {
            console.log('error')
        }

    }, [])

    return [messages, value, setValue, prevValue, connected];
};

export default UseWebSocket;