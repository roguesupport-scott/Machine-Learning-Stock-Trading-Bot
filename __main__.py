import alpaca_trade_api as tradeapi
from forecast_library import *
from config import *
import sys

def buy():
    # Searching for Optimistic Twits from Automated Stock Alert Accounts
    twit_data = importing_twitdata('topstockalert', 'StockAuthority')
    # Candidate Stocks Selected By Sentiment Analysis on Twit Data
    candidate_stocks = twit_sentiment_analyzer(twit_data)
    # Analyzing Candidate Stocks with Historical Data
    for ticker in candidate_stocks.difference(my_positions):
        stock_history = pulling_price_history(ticker)
        current_price = float(stock_history['close'].head(1))
        # Predicting Future Stock Price with Machine Learning
        target_price = float(random_forest_forecast(stock_history))
        # Determining Num of Shares to Buy
        if buying_power < 200:
            qty_desired = int((buying_power/current_price) / len(candidate_stocks.difference(my_positions)))
        else:
            qty_desired = int(((target_price - current_price) / current_price) * buying_power)
        # Submitting Buy Order
        if buying_power >= target_price*qty_desired > current_price*qty_desired:
            alpaca_api.submit_order(
                symbol=ticker,
                qty=qty_desired,
                side='buy',
                type='market',
                time_in_force='gtc'
                )
    return print('Buy Orders Sent')


def sell():
    # Selling Positions on Newly Updated Target Price or Unexpected Loss of 7.5% or More
    for position in my_positions.difference(my_orders):
        # Forecasting with Updated Data
        stock_history = pulling_price_history(position)
        current_price = float(alpaca_api.get_position(position).current_price)
        # Updating Future Stock Price with Machine Learning
        target_price = float(random_forest_forecast(stock_history))
        price_change = float(alpaca_api.get_position(position).unrealized_plpc)
        qty_bought = float(alpaca_api.get_position(position).qty)

        # Sell on 7.5% Loss or 35% Profit (due to unexpected spikes)
        if price_change < -0.075 or price_change > 0.35:
            alpaca_api.submit_order(
                symbol=position,
                qty=qty_bought,
                side='sell',
                type='market',
                time_in_force='gtc'
            )
        # Selling on Target Price or Acceptable Loss
        else:
            stop_price = round(current_price * 0.925, 4)
            alpaca_api.submit_order(
                symbol=position,
                qty=qty_bought,
                side='sell',
                type='stop_limit',
                limit_price=target_price,
                stop_price=stop_price,
                time_in_force='gtc'
            )
    return print('Sell Orders Sent')


if __name__ == '__main__':
    # Account Status Review
    alpaca_api = tradeapi.REST(base_url=ALPACA_BASE_URL,
                        key_id=ALPACA_API_KEY,
                        secret_key=ALPACA_SECRET_KEY
                        )
    # Liquidity
    buying_power = float(alpaca_api.get_account().buying_power)
    # Positions Held
    my_positions = set()
    open_positions = alpaca_api.list_positions()
    if len(open_positions) > 0:
        for index in range(len(open_positions)):
            my_positions.add(open_positions[index].symbol)
    # Orders Inplace
    my_orders = set()
    open_orders = alpaca_api.list_orders(status='open')
    if len(open_orders) > 0:
       for index in range(len(open_orders)):
          my_orders.add(open_orders[index].symbol)
    # Executing Sell & Buy Orders
    sell()
    buy()
    sys.exit()
