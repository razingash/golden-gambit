
## QuickStart
### ordinary
1) in macroeconomics_simulator directory run 
    - pip install -r requirements/windows.txt  **choose 'windows' or 'unix'**
    - python manage.py initialization
    - - this command will implement database
2) in frontend directory run npm start
- site will be available at http://localhost:3000

### using docker
1) docker compose build
2) docker compose up
- site will be available at http://localhost:3001

### using kubernetes
1) build images for kubernetes services
   - docker build -f ../macroeconomics_simulator/Dockerfile -t kuber_macroeconomics_simulator:latest ../macroeconomics_simulator
   - docker build -f ../frontend/Dockerfile.prod -t kuber_frontend:latest ../frontend
2) minikube start --driver=docker
3) load images into minicube
   - docker context use default
   - minikube image load kuber_macroeconomics_simulator:latest
   - minikube image load kuber_frontend:latest
4) kubectl apply -f .
   - should be done sequentially: infrastructure -- databases 
   -- app -- network -- queue -- monitoring
5) kubectl get pods -n frontend -l app=nginx
6) kubectl port-forward pod/<pod-name> 80:80 -n frontend
- site will be available at http://localhost:80

### notifications
1) if you want to recreate database in ordinary version run python manage.py reinitialization


## need to know
1) useEffect has a missing dependency: "fetch...". Either include it or remove the dependency array
   - this error doesn't pose a threat because the "fetch..." function itself is always used
     through the custom useFetching hook, which allows you to call this request when it is 
     actually necessary, using the errors encountered and the progress of the request

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
   - if the owner of specific shares is also the owner of this company, then the money from dividends will go to
   the company’s account, which will provoke users to buy shares of other companies in order to buy gold from
   dividends with silver, which will need to be deposited into the company’s account in order to receive
   a tiny (but more or less stable) passive income
4) ownership
   - The company can be lost if
   - - company won't be able to pay obligations (dividends) to all shareholders
   - - the owner will lose the largest percentage of shares
5) tier
   - to increase the company's tier you need to sacrifice other companies to merge
   - when merging companies, the shares of shareholders will be transferred to the new company
6) value
   - depends on what product the company produces, current events, the amount of gold in the company
7) registration of a new company
   - player can register 1 company for free. If he has already registered a company,
then he will need to deposit an amount in silver equivalent to the value of 100 gold.
