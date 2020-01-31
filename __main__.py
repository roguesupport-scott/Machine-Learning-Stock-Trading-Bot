import alpaca_trade_api as tradeapi
import numpy as np
from forecast_library import *
from config import *
import sys

def buy():
    # Searching for Optimistic Twits from Automated Stock Alert Accounts
    twit_data = importing_twitdata('topstockalert', 'StockAuthority')
    # Candidate Stocks Selected By Sentiment Analysis on Twit Data
    candidate_stocks = twit_sentiment_analyzer(twit_data)
    # Analyzing Candidate Stocks with Historical Data
    for ticker in candidate_stocks:
        # Preventing Overcommitting on Specific Equity
        if ticker not in my_positions:
            stock_history = stock_price_history(ticker)
            current_price = float(stock_history['close'].head(1))
            # Predicting Future Stock Price with Machine Learning
            target_price = float(random_forest_forecast(stock_history))
            # Determining Num of Shares to Buy
            if buying_power < 300:
                qty_desired = round((buying_power / current_price) - 0.5)
            else:
                qty_desired = round(((target_price - current_price) / current_price) * buying_power)
        # Submitting Buy Order
            if float(account.buying_power) > target_price > current_price:
                return api.submit_order(
                        symbol=ticker,
                        qty=qty_desired,
                        side='buy',
                        type='market',
                        time_in_force='gtc'
                        )

def sell():
    # Selling Positions on Target Price or Unexpected Loss of 7% or More
    for position in my_positions:
        # Forecasting with Updated Data
        stock_history = stock_price_history(position)
        current_price = float(api.get_position(position).current_price)
        # Updating Future Stock Price with Machine Learning
        target_price = float(random_forest_forecast(stock_history))
        price_change = float(api.get_position(position).unrealized_plpc)
        qty_bought = float(api.get_position(position).qty)

        # Sell on 7.5% Loss or More
        if price_change < -0.075:
            return api.submit_order(
                        symbol=position,
                        qty=qty_bought,
                        side='sell',
                        type='market',
                        time_in_force='cls'
                        )
        # Sell Stop Loss On Uptrend or Little Loss
        else:
            stop_price = round(current_price * (1 - (-0.075 - price_change)), 4)
            return api.submit_order(
                    symbol=position,
                    qty=qty_bought,
                    side='sell',
                    type='stop_limit',
                    limit_price=target_price,
                    stop_price=stop_price,
                    time_in_force='cls'
                    )


if __name__ == '__main__':
    # Account Status Review
    api = tradeapi.REST(base_url=ALPACA_BASE_URL, key_id=ALPACA_API_KEY, secret_key=ALPACA_SECRET_KEY)
    account = api.get_account()
    buying_power = float(account.buying_power)
    my_positions = []
    if len(api.list_positions()) != 0:
        for i in np.arange(len(api.list_positions())):
            my_positions.append(api.list_positions()[i].symbol)
    # Executing Orders
    sell()
    buy()
    sys.exit()