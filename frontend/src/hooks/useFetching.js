import {useState} from "react";

export const useFetching = (callback, delay=0) => {
    const [isLoading, setIsLoading] = useState(null);
    const [error, setError] = useState(null);
    const [isSpammed, setIsSpammed] = useState(null);

    const fetching = async (...args) => {
        if (isSpammed) return;
        try {
            setIsSpammed(true);
            setIsLoading(true);
            setError(false);
            return await callback(...args);
        } catch (e) {
            console.log(e.status, e)
            setError(true);
        } finally {
            setIsLoading(false);
            setTimeout(() => {
                setIsSpammed(false);
            }, delay);
        }
    }

    return [fetching, isLoading, error];
};