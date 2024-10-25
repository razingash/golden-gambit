import React, {useEffect, useRef, useState} from 'react';
import {baseSseURL} from "./useApiInterceptor";

const UseEventSourcing = (event_url, key) => {
    const [messages, setMessages] = useState([]); //Let it be for now, maybe remove it in the future
    const [value, setValue] = useState(null); // can be used to set the initial value
    const eventSourceRef = useRef(null); // necessary to close the connection

    const subscribe = async () => {
        if (eventSourceRef.current || localStorage.getItem(key)) return;

        const eventSource = new EventSource(`${baseSseURL}${event_url}`);
        eventSourceRef.current = eventSource;

        eventSource.onmessage = (event) => {
            //console.log(event)
            let message = event.data;
            message = JSON.parse(message.replace(/'/g, '"'));
            setMessages(prev => [message, ...prev])
            setValue(message);

            localStorage.setItem(key, JSON.stringify(message));
        }

        eventSource.onerror = (error) => {
            console.error('Error SSE:', error);
            eventSource.close();
            localStorage.removeItem(key)
        }
    }

    const closeConnection = async () => {
        if (eventSourceRef.current) {
            eventSourceRef.current.close();
            eventSourceRef.current = null;
            localStorage.removeItem(key);
        }
    }

    useEffect(() => {
        const existingConnection = localStorage.getItem(key);

        if (!existingConnection) {
            void subscribe();
        } else {
            const storedMessage = JSON.parse(existingConnection);
            setMessages(prev => [storedMessage, ...prev]);
            setValue(storedMessage);
        }

        const handleUnload = () => {
            void closeConnection();
        }

        window.addEventListener('beforeunload', handleUnload);
        window.addEventListener('unload', handleUnload);

        return () => {
            void closeConnection();
            window.addEventListener('beforeunload', handleUnload);
            window.addEventListener('unload', handleUnload);
        }
    }, [event_url])

    useEffect(() => {
        const handleStorage = (e) => { // updating data for non-primary tabs
            if (e.key === key && e.newValue) {
                const message = JSON.parse(e.newValue);
                setMessages(prev => [message, ...prev])
                setValue(message);
            }
        }

        window.addEventListener('storage', handleStorage);

        return () => {
             window.removeEventListener('storage', handleStorage);
        }
    }, [key])

    return [messages, value, setValue];
};

export default UseEventSourcing;