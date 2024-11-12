import React, {useState} from 'react';

export const useInput = (initialValue) => {
    const [value, setValue] = useState(initialValue);
    console.log(0)
    const onChange = e => {
        console.log(1)
        setValue(e.target.value)
    }

    return {value, onChange}
};

export default useInput;