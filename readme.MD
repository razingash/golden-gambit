
## QuickStart
### ordinary
1) In the `macroeconomics_simulator` directory run:

   ```bash
   pip install -r requirements/windows.txt  # Choose 'windows' or 'unix'
2) In the `frontend` directory run 

   ```bash
   npm start
- site will be available at http://localhost:3000

### using docker
In the project directory run

    docker compose build
    docker compose up
- site will be available at http://localhost:3001

### using kubernetes
1) build images for kubernetes services `from k8s directory`
   ```bash
   docker build -f ../macroeconomics_simulator/Dockerfile -t kuber_macroeconomics_simulator:latest ../macroeconomics_simulator
   ```
   ```bash
   docker build -f ../frontend/Dockerfile.prod -t kuber_frontend:latest ../frontend
2) run minikube
   ```bash 
   minikube start --driver=docker
3) load images into minicube
   ```bash
   docker context use default
   ```
   ```bash
   minikube image load kuber_macroeconomics_simulator:latest
   ```
   ```bash
   minikube image load kuber_frontend:latest
4) consistently apply dependencies in directories: infrastructure -- databases
   -- app -- network -- queue -- monitoring
   ```bash
   kubectl apply -f .
5) kubectl get pods -n frontend -l app=nginx
6) kubectl port-forward pod/<pod-name> 80:80 -n frontend
- site will be available at http://localhost:80

### notifications
- If you want to recreate database in ordinary version run python manage.py reinitialization
- I decided not to auto-create dashboards in Grafana to avoid overloading the repository with redundant data. Instead, to visualize metrics, it would be easiest to import specific dashboards, such as 3662 for Minikube and 747 for Kubernetes pods.

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
