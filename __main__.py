import alpaca_trade_api as tradeapi
import pandas as pd
from forecast_library import *
from config import *
import os
import sys

def buy():
    # Importing Tweets Data from StockTwit Accounts
    twit_data = importing_twitdata('StockAuthority', 'topstockalert') #Handpicked Accounts to Get JSON
    # Candidate Stocks Selected By Sentiment Analysis on Optimistic Tweets
    candidate_stocks = twit_sentiment_analyzer(twit_data)
    # Opening Text File To Store Target Pricing
    f = open("target_price_list.txt", "a")
    # Analyzing Candidate Stocks (Not Currently Held in Position) with Historical Data
    for ticker in candidate_stocks.difference(my_positions):
        try:
            stock_history = pulling_price_history(ticker)
            current_price = float(stock_history['close'].head(1))
            # Predicting Future Stock Price with Machine Learning Random Forest Regressor Model
            target_price = float(random_forest_forecast(stock_history))
            # Determining Num of Shares to Buy
            if buying_power > 200.00:
                qty_desired = int(round(((target_price - current_price) / current_price) * buying_power)) - 1
            else:
                qty_desired = int((buying_power/current_price)) - 1
            # Submitting Affordable Buy Order on Market Price
            if buying_power >= (current_price * qty_desired) and qty_desired > 0:
                alpaca_api.submit_order(
                    symbol=ticker,
                    qty=qty_desired,
                    side='buy',
                    type='market',
                    time_in_force='gtc'
                    )
                # Save Target Price on a Separate Text File
                f.write(ticker + " " + str(target_price) + "\n")
        # Eliminating Human Error in Collected Tweet Data
        except (IndexError or ValueError):
            pass
    f.close()
    return print('Buy Orders Sent')


def sell():
    # Opening Saved File of Target Price List (Saved from Previous Trading Day)
    f = open('target_price_list.txt', 'r+')
    if os.stat('target_price_list.txt').st_size != 0:
        f_content = f.readlines()
        df = pd.DataFrame({'ticker': f_content}).ticker.str.split(" ", expand=True)
        # Selling Positions that Does Not Have Pending Selling Orders
        for position in my_positions.difference(my_orders):
            # Importing Position Data
            position_api = alpaca_api.get_position(position)
            price_change = float(position_api.unrealized_plpc)
            current_price = float(position_api.current_price)
            qty_bought = float(position_api.qty)
            try:
                target_price = float(df.loc[df[0] == str(position), 1].values[0][:6])
                # Sell on 7.5% Loss, Inverted Targeted Percent Loss, or Targeted Profit
                if price_change <= -0.075 or current_price >= target_price:
                    alpaca_api.submit_order(
                        symbol=position,
                        qty=qty_bought,
                        side='sell',
                        type='market',
                        time_in_force='gtc'
                    )
                    # Omitting Sold Position Data from 'target_price_list.txt'
                    f.seek(0, 0)
                    for line in f_content:
                        if str(position).lower() not in line.lower().split(" "):
                            f.write(line)
                    f.truncate()
            except (IndexError or ValueError):
                alpaca_api.submit_order(
                    symbol=position,
                    qty=qty_bought,
                    side='sell',
                    type='market',
                    time_in_force='gtc'
                )
                f.seek(0, 0)
                for line in f_content:
                    if str(position).lower() not in line.lower().split(" "):
                        f.write(line)
                f.truncate()

    # Closing Text File
    f.close()
    return print('Sell Orders Sent')

# Main Function
if __name__ == '__main__':
    # Connecting to Alpaca Account
    alpaca_api = tradeapi.REST(
        base_url=ALPACA_BASE_URL,
        key_id=ALPACA_API_KEY,
        secret_key=ALPACA_SECRET_KEY
        )
    # Liquidity
    buying_power = float(alpaca_api.get_account().buying_power)
    # Current Holding Positions
    open_positions = alpaca_api.list_positions()
    my_positions = set(map(lambda index: open_positions[index].symbol, range(len(open_positions))))
    # Open Orders
    open_orders = alpaca_api.list_orders(status='open')
    my_orders = set(map(lambda index: open_orders[index].symbol, range(len(open_orders))))
    # Executing Sell & Buy Orders
    sell()
    buy()
    sys.exit()

