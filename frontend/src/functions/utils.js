
export const formatNumber = (num) => {
    if (num >= 1e9) {
        return (num / 1e9).toFixed(1) + 'B';
    } else if (num >= 1e6) {
        return (num / 1e6).toFixed(1) + 'M';
    } else if (num >= 1e3) {
        return (num / 1e3).toFixed(1) + 'K';
    }
    return num.toString();
}

export const formatTimestamp = (timestamp) => {
    const date = new Date(timestamp * 1000);
    return date.toLocaleDateString([],
        {hour:'2-digit',  minute:'2-digit',  day:'2-digit',  month:'2-digit',  year:'numeric'});
}

export const percentageOfNumber = (num1, num2) => {
    return (100 - (num1 * 100 / num2).toFixed(2)).toFixed(2)
};

export const calculateFluctuations = (num1, num2) => {
    return ((num1 - num2) / 100).toFixed(2)
}

export const calculateWealth = (silver, gold, goldRate) => {
    return (+silver + +gold * goldRate).toFixed(2)
}

export const selectSharesType = { "ordinary": 1, "preferred": 2 };
export const selectTradingType = { "purchase": "buy", "sale": "sell" };

export const decodeSharesType = (num) => {
    const data = {1: 'ordinary', 2: 'preferred'}
    return data[num] || 'incorrect data was transmitted';
}

export const decodeCompanyType = (num) => {
    const data = {
        1: "farm", 2: "fish farm", 3: "mine", 4: "ore mine", 5: "quarry", 6: "sawmill", 7: "plantation",
        8: "food factory", 9: "deep sea fishing enterprise", 10: "chemical plant", 11: "metallburgical plant",
        12: "brick factory", 13: "glass factory", 14: "wood processing plant", 15: "textile factory",
        16: "pharmaceutical company", 17: "microelectonics production plant", 18: "engineering plant",
        19: "furniture factory", 20: "clothing factory", 21: "oil company", 22: "oil refining company",
        23: "defense industry", 24: "construction company", 25: "clothing factory 2"
    }
    return data[num] || 'incorrect data was transmitted';
}

export const decodeProductType = (num) => {
    const data = {
        1: "unprocessed food", 2: "minerals", 3: "base metals", 4: "slate", 5: "limestone", 6: "clay", 7: "wood",
        8: "construction raw materials", 9: "processed food", 10: "chemicals", 11:" processed metals",
        12: "building materials", 13: "processed wood", 14:" textile", 15: "medicines", 16: "microelectronics",
        17: "mechanical parts", 18: "furnitures", 19: "clothing", 20: "oil", 21: "special clothing", 22: "weapons",
        23: "fuel",
    }
    return data[num] || 'incorrect data was transmitted';
}

export const decodeEventType = (num) => {
    const data = {
        1: 'Crop Failure', 2: 'Rich Harvest', 3: 'Earthquake', 4: 'Flood', 5: 'Extreme heat', 6: 'Drought',
        7: 'Forest Fires', 8: 'Epidemic', 9: 'Pandemic Outbreak', 10: 'Workers’ Strikes', 11: 'Protests',
        12: 'Civil War', 13: 'War'
    }
    return data[num] || 'incorrect data was transmitted';
}

export const decodeEventState = (num) => {
    const data = {2: 'beginning', 3: "culmination", 4: "consequences"}
    return data[num] || 'incorrect data was transmitted';
}