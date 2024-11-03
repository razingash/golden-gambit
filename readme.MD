
## QuickStart
### ordinary
1) in macroeconomics_simulator directory run 
    - pip install -r requirements.txt
    - python manage.py initialization
    - - this command will implement database
2) in frontend directory run npm start
3) site will be available at http://localhost:3000

### using docker
1) docker compose build
2) docker compose up
3) site will be available at http://localhost:3000

### notifications
1) if you want to recreate database in ordinary version run python manage.py deinitialization


## need to know
1) useEffect has a missing dependency: 'fetch...'. Either include it or remove the dependency array
   - this error doesn't pose a threat because the fetch... function itself is always used
     through the custom useFetching hook, which allows you to call this request when it is 
     actually necessary

# Description

### role of currency
1) gold
   - there is a limited amount of gold for sale, about a billion
   - the price of gold depends on the amount of gold available in the market
   - brings a small passive income for the company so that the company can exist on its own for some time
2) silver
   - silver is a limitless currency for which all transactions are made

### events
- events affect the prices of goods and the productive capacity of the company,
which in turn affects the overall value of the company

### companies
1) shares
   - ordinary shares are used to pay dividends in silver
2) preferred shares
   - preferred shares influence leadership in the company
3) dividendes
   - dividend percentage is set by the owner of the company, minimum - 2%
   - paid daily
4) ownership
   - The company can be lost if
   - - won't be able to pay obligations (dividends) to all shareholders
   - - the owner will lose the largest percentage of shares
5) tier
   - to increase the company's tier it is necessary to sacrifice other companies to merge
   - when merging companies, the shares of shareholders will be transferred to the new company
6) value
   - depends on what product the company produces, current events, the amount of gold in the company
7) registration of a new company
   - player can register 1 company for free, then he will need to deposit an amount
   in silver which will be equivalent to the cost of 100 gold
