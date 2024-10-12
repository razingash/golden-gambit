import React, {useState} from 'react';

const SelectCompaniesForm = ({userCompanies, companyType, sacrificesAmount, onSelectCompanies}) => {
    const [selectedCompanies, setSelectedCompanies] = useState(Array(sacrificesAmount).fill(''));

    const handleSelectedChange = (index, value) => {
        const updateSelected = [...selectedCompanies];
        updateSelected[index] = value;
        setSelectedCompanies(updateSelected);
        onSelectCompanies(updateSelected);
    }

    const filteredCompanies = userCompanies && userCompanies.filter(company => company.type === companyType);

    if (filteredCompanies.length === 0) {
        return <div>not enough companies</div>
    }

    return (
        <div>
            {Array.from({ length: sacrificesAmount }).map((_, index) => (
                <select key={index} value={selectedCompanies[index]} onChange={(e) => handleSelectedChange(index, e.target.value)}>
                    {filteredCompanies.map((company) => (
                        <option key={company.ticker} value={company.name}>{company.name} ({company.ticker})</option>
                    ))}
                </select>
            ))}
        </div>
    );
};

export default SelectCompaniesForm;