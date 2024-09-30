from stock.models import GoldSilverExchange
"""
after API, optimize via clickhouse or redis fow webhooks
"""

def fast_calculate_gold_price(instance: GoldSilverExchange, amount_of_gold):
    affordable_gold = instance.amount
    gold_price = instance.current_price
    base_price = 1000
    fluctuation_level = gold_price * (amount_of_gold / affordable_gold)
    gold_rate = base_price * (100 - fluctuation_level) / 100 # new gold price
    instance.current_price = gold_rate
    #no need for saving data
    return fluctuation_level, gold_rate

