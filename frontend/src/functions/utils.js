
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

export const percentageOfNumber = (num1, num2) => {
    return Math.round(num1 * 100 / num2)
}

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
