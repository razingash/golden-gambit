import React, {useEffect, useRef, useState} from 'react';

const UseEventSourcing = (event_url) => {
    const [messages, setMessages] = useState([]); //Let it be for now, maybe remove it in the future
    const [value, setValue] = useState(null); // can be used to set the initial value
    const eventSourceRef = useRef(null);

    const subscribe = async () => {
        if (eventSourceRef.current) return;

        const eventSource = new EventSource(event_url);
        eventSourceRef.current = eventSource;

        eventSource.onmessage = (event) => {
            //console.log(event)
            let message = event.data;
            message = JSON.parse(message.replace(/'/g, '"'));
            setMessages(prev => [message, ...prev])
            setValue(message);
        }

        eventSource.onerror = (error) => {
            console.error('Error SSE:', error);
            eventSource.close();
        }
    }

    const closeConnection = async () => {
        if (eventSourceRef.current) {
            eventSourceRef.current.close();
            eventSourceRef.current = null;
        }
    }

    useEffect(() => {
        void subscribe();

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

    return [messages, value, setValue];
};

export default UseEventSourcing;