import {useCallback, useState} from "react";

export const useFetching = (callback, delay=0) => {
    const [isLoading, setIsLoading] = useState(null);
    const [error, setError] = useState(null);
    const [isSpammed, setIsSpammed] = useState(null);
    // useCallback может быть неоправдан если useFetching не используется в useEffect
    const fetching = useCallback(async (...args) => {
        if (isSpammed) return;
        console.log('usefetching')
        try {
            setIsSpammed(true);
            setIsLoading(true);
            return await callback(...args);
        } catch (e) {
            console.log(e?.status, e)
            console.log(e?.response?.data)
            setError(e?.response?.data);
        } finally {
            setIsLoading(false);
            setTimeout(() => {
                setIsSpammed(false);
            }, delay);
        }
    }, [callback, delay, isSpammed]);

    return [fetching, isLoading, error];
};