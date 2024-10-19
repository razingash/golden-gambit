import React, {useEffect, useRef, useState} from 'react';
import {domenURL} from "./useApiInterceptor";

const UseWebSocket = (link) => {
    const [messages, setMessages] = useState([]);
    const [value, setValue] = useState(null);
    const [connected, setConnected] = useState(false);
    const socketRef = useRef();

    useEffect(() => {
        socketRef.current = new WebSocket(`${domenURL}${link}`)

        socketRef.current.onopen = () => {
            console.log('connected')
            setConnected(true);
            const message = {
                event: 'connection'
            }
            socketRef.current.send(message);
        }

        socketRef.current.onmessage = (event) => {
            const message = event.data
            console.log(message)
            setMessages(prev => [message, ...prev])
            setValue(message);
        }

        socketRef.current.onclose = () => {
            console.log('closing')
        }

        socketRef.current.onerror = () => {
            console.log('error')
        }

    }, [])

    return [messages, value, setValue, connected];
};

export default UseWebSocket;