"""there will be no action like creating a new company"""
from services.company.C_services import buy_products, sell_products
from services.stock.S_services import purchase_gold, sell_gold

"""REMOVE ALL THIS LATER"""

# gold actions

def action_buy_gold(user_id, amount) -> None: # expedience = 0
    purchase_gold(user_id=user_id, amount=amount)

def action_sell_gold(user_id, amount) -> None: # expedience = 0
    sell_gold(user_id=user_id, amount=amount)

# shares actions
"""too long to do, given that the entire system with pseudo-bots is unnecessary and will be removed"""

# products actions

def action_buy_cheap_products(company_ticker, product_type, amount) -> None: # expedience = 1
    buy_products(company_ticker, product_type, amount)

def action_buy_expensive_products(company_ticker, product_type, amount) -> None: # expedience = -1
    buy_products(company_ticker, product_type, amount)

def action_sell_cheap_products(company_ticker, product_type, amount) -> None: # expedience = -1
    sell_products(company_ticker, product_type, amount)

def action_sell_expensive_products(company_ticker, product_type, amount) -> None: # expedience = 1
    sell_products(company_ticker, product_type, amount)
