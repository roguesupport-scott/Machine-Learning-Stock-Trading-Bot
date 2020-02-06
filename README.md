# Machine-Learning-Stock-Trading-Bot
Objective: 
Day trading bots are ubiquitous projects. 
Swing trading bots are not as common, especially one that performs both fundamental and technical trading methodology with machine learning implementation. Staying true to its swing trading objective, the program is only designed to execute selling and buying once per day. 

Mechanics: 
Implements sentiment analysis on equity related "twits" to identify optimistically trending stocks
Performs data collecting and scrubbing of 3 months worth of price history, press release, sentiment polarity, and subjectivity data
Predicts and calculates target price through machine learning random forest model for the next 20 business days  

a.) config.py -- Storage of all api keys: ALPHA VANTAGE, NEWSAPI, ALPACA

b.) forecast_library.py -- Data scrubbing and machine learning function
  
  1. def importing_twitdata(id1, id2) 
      --> Imports stocktwit data from 2 different automated accounts that posts daily trending stocks 
          Data is scrubbed by deleting twits that does not literally contain the ticker symbol of a stock
  
  2. def twit_sentiment_analyzer(raw_data) 
      --> Uses TextBlob to determine the twits sentiment on particular stocks
      --> Disregards any twit with polarity lower than 0.4 (Polarity ranges from (negative) -1 to 1 (positive))
      
  3. def pulling_price_history(ticker)
      --> Pulls the latest 3 months data of stock price history from alphavantage and puts into a DataFrame
      --> Supplements DataFrame by adding press release dates and news sentimentality and subjectivity to the DataFrame 
      --> NewsAPI data was stored in clustered dictionary and list; thus it was hectic handpicking appropriate sections of data
      --> Format and scrub DataFrame so that it is ready for machine learning
   
  4. def random_forest_forecast(data)
      --> Chose the random forest regressor model for its powerful prediction capability on short term forecasts and limited data
      --> Lacking data (merely 3 months worth of stock price history) discouraged implementing other model (free open data was used)
      --> Random forest regressor had the highest score
      --> Train 80% of the data and tested 20%
      --> Predicts the stock's price for the next 20 business days and return the maximum price multiplied by it's confidence level
         
c.) __main__.py -- Executing Trade on Alpaca (https://alpaca.markets/)
   
   1. def buy()
      --> Executes created functions in forecast_library.py in the following order:
          *def importing_twitdata(id1, id2) 
          *def twit_sentiment_analyzer(raw_data)
          *for each candidate stock, the bot avoids buying stocks already in position, calculates number of shares to buy
          qty_desired = round(((target_price - current_price) / current_price) * buying_power), and checks if the portfolio
          can afford to make an order
          
   2. def sell()
       --> Selling positions held from the previous night
       --> Uses the same function as def buy() to update target price with new data available to increase accuracy
       --> If position has more than 7.5% loss, the bot orders an immediate sell order on market price
       --> Else, the bot pushes stop/limit order: 
            limit order = newly updated target price  
            stop limit = -7.5% of current price

    3. if __name__ == '__main__':
    # Account Status Review
    alpaca_api = tradeapi.REST(base_url=ALPACA_BASE_URL,
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
