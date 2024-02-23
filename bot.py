import telebot
from geckoterminal_api import GeckoTerminalAPI
import time
import os
import threading

gt = GeckoTerminalAPI()

TOKEN = os.environ.get("PTRADE_KEY")
bot = telebot.TeleBot(TOKEN)

TON_TOKEN_ADDRESS = "EQAaV7Q9M0vrO5HfKrPNnQneXB-S9RyBneMNeX4KzECIYrdk"
POOL_ADDRESS = "EQA5ieb1PvkulegIa_N06geN0WrdcBT9k34y62qU8yIqqM3b"
INTERVAL = 3600

prices = []
volumes = []
runs = 0

def fetch_pool_info():
    try:
        pair_info = gt.network_pool_address("ton", POOL_ADDRESS)
        return pair_info["attributes"]
    except KeyError as err:
        print(repr(err))
        print(pair_info)

def calculate_ma(prices, periods):
    return sum(prices[-periods:]) / periods

def calculate_vwap(prices, volumes):
    return sum(price * volume for price, volume in zip(prices, volumes)) / sum(volumes)

def analyze_pnd(price_change_percentage):
    change_percentage = price_change_percentage["h1"]
    if change_percentage > 5:
        return "Sell"
    elif change_percentage < -5:
        return "Buy"
    else:
        return "Hold"

def analyze_ma(ma_short, ma_long):
    if ma_short > ma_long:
        return "Buy"
    elif ma_short < ma_long:
        return "Sell"
    else:
        return "Hold"

def analyze_vwap(prices, volumes):
    vwap = calculate_vwap(prices, volumes)
    current_price = prices[-1]
    if current_price < vwap:
        return "Buy"
    elif current_price > vwap:
        return "Sell"
    else:
        return "Hold"

def start(bot, wait_time):
    global prices, volumes, runs
    while True:
        info = fetch_pool_info()
        price_usd = info["base_token_price_usd"]
        price_quote = info["base_token_price_quote_token"]
        price_change_percentage = info["price_change_percentage"]
        volumes.append(info["volume_usd"]["h1"])
        prices.append(price_quote)

        if runs > 0:
            if runs > 12:
                ma_short = calculate_ma(prices, 8)
                ma_long = calculate_ma(prices, 12)
                hint_ma = analyze_ma(ma_short, ma_long)
            hint_pnd = analyze_pnd(price_change_percentage)
            hint_vwap = analyze_vwap(prices, volumes)

            resp = f"Pool: {info['name']}\n"
            resp += f"Price: {round(price_quote, 4)} (${round(price_usd, 4)})\n\n"

            resp += f"Price changes:\n"
            resp += f"1H: {price_change_percentage['h1']}\n"
            resp += f"24H: {price_change_percentage['h24']}\n\n"
            
            if runs > 12:
                resp += f"MA Hint: {hint_ma}\n"

            resp += f"PnD Hint: {hint_pnd}\n"
            resp += f"VWAP Hint: {hint_vwap}\n"
            
            bot.send_message("-4123823427", resp)

        runs += 1
        time.sleep(wait_time)

thread = threading.Thread(target=start, args=(bot, INTERVAL,))
thread.start()

bot.infinity_polling()
thread.join()
