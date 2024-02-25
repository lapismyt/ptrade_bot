import telebot
from geckoterminal_api import GeckoTerminalAPI
import time
import os
import threading

gt = GeckoTerminalAPI()

TOKEN = os.environ.get("PTRADE_KEY")
bot = telebot.TeleBot(TOKEN)

POOL_ADDRESS = os.environ.get("PTRADE_POOL")
INTERVAL = 3600

prices = []
volumes = []
runs = 0

def fetch_pool_info():
    try:
        pair_info = gt.network_pool_address("ton", POOL_ADDRESS)
        return pair_info["data"]["attributes"]
    except KeyError as err:
        print(repr(err))
        print(pair_info)

def calculate_ma(prices, periods):
    return sum(prices[-periods:]) / periods

def calculate_vwap(prices, volumes):
    return sum(price * volume for price, volume in zip(prices, volumes)) / sum(volumes)

def analyze_pnd(change_percentage):
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
        price_usd = float(info["base_token_price_usd"])
        price_quote = float(info["base_token_price_quote_token"])
        price_change_percentage_h1 = float(info["price_change_percentage"]["h1"])
        price_change_percentage_h24 = float(info["price_change_percentage"]["h24"])
        volumes.append(float(info["volume_usd"]["h1"]))
        prices.append(price_quote)

        if runs > 0:
            if runs > 6
                ma_short = calculate_ma(prices, 2)
                ma_long = calculate_ma(prices, 6)
                hint_ma = analyze_ma(ma_short, ma_long)
            hint_pnd = analyze_pnd(price_change_percentage_h1)
            hint_vwap = analyze_vwap(prices, volumes)

            resp = f"Pool: {info['name']}\n"
            resp += f"Price: {round(price_quote, 4)} (${round(price_usd, 4)})\n\n"

            resp += f"Price changes:\n"
            resp += f"1H: {round(price_change_percentage_h1, 2)}\n"
            resp += f"24H: {round(price_change_percentage_h24, 2)}\n\n"
            
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
