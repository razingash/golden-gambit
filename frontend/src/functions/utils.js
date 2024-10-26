
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

export const sharesTypes = { "ordinary": 1, "preferred": 2 };

export const tradingTypes = { "purchase": "buy", "sale": "sell" };

export const decodeSharesType = (num) => {
    switch (num) {
        case 1:
            return 'ordinary'
        case 2:
            return 'preferred'
    }
}

export const decodeCompanyType = (num) => {
    switch (num) {
        case 1:
            return "farm"
        case 2:
            return "fish farm"
        case 3:
            return "mine"
        case 4:
            return "ore mine"
        case 5:
            return "quarry"
        case 6:
            return "sawmill"
        case 7:
            return "plantation"
        case 8:
            return "food factory"
        case 9:
            return "deep sea fishing enterprise"
        case 10:
            return "chemical plant"
        case 11:
            return "metallburgical plant"
        case 12:
            return "brick factory"
        case 13:
            return "glass factory"
        case 14:
            return "wood processing plant"
        case 15:
            return "textile factory"
        case 16:
            return "pharmaceutical company"
        case 17:
            return "microelectonics production plant"
        case 18:
            return "engineering plant"
        case 19:
            return "furniture factory"
        case 20:
            return "clothing factory"
        case 21:
            return "oil company"
        case 22:
            return "oil refining company"
        case 23:
            return "defense industry"
        case 24:
            return "construction company"
        case 25:
            return "clothing factory 2"
    }
}

export const decodeProductType = (num) => {
    switch (num) {
        case 1:
            return "unprocessed food"
        case 2:
            return "minerals"
        case 3:
            return "base metals"
        case 4:
            return "slate"
        case 5:
            return "limestone"
        case 6:
            return "clay"
        case 7:
            return "wood"
        case 8:
            return "processed food"
        case 9:
            return "chemicals"
        case 10:
            return "processed metals"
        case 11:
            return "building materials"
        case 12:
            return "processed wood"
        case 13:
            return "textile"
        case 14:
            return "medicines"
        case 15:
            return "microelectronics"
        case 16:
            return "mechanical parts"
        case 17:
            return "furnitures"
        case 18:
            return "clothing"
        case 19:
            return "oil"
        case 20:
            return "special clothing"
        case 21:
            return "weapons"
        case 22:
            return "fuel"
        case 23:
            return "construction raw materials"
    }
}
