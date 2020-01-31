# Machine-Learning-Stock-Trading-Bot
Objective: C++ day trading bots are such ubiquitous projects. 
Swing trading bots are not as common, especially one that performs both fundamental and technical trading methodology. 
This bot trades in the interval of 1-20 business days. The bot is designed to ran once a day.
Task Scheduler will do the job for automated python script runs.

Mechanics: Implements sentiment analysis on equity related "twits" to identify upward trending stocks 
Performs fundamental trading methodology by collecting 3 months worth of stock price history and press releases 
Predicts and calculates target price through machine learning random forest model for the next 20 business days

a.) config.py -- Storage of all api keys: ALPHA VANTAGE, NEWSAPI

b.) forecast_library.py -- Data scrubbing and machine learning function
  
  1. def importing_twitdata(id1, id2) 
      --> Imports stocktwit data from 2 different automated accounts that posts trending stocks. 
          Data is scrubbed by deleting twits that does not literally has the ticker symbol of a stock
  
  2. def twit_sentiment_analyzer(raw_data) 
      --> Uses TextBlob to determine the twits sentiment on particular stocks
      --> Disregards any twit with polarity lower than 0.4 (Polarity ranges from (negative) -1 to 1 (positive))
      
  3. def stock_price_history(ticker)
      --> Pulls the latest 3 months data of stock price history from alphavantage and put into DataFrame
      --> Supplements dataframe by adding press release dates and press release sentimentality and subjectivity to the DataFrame 
      --> NewsAPI data was stored in clustered dictionary and list; thus it was hectic handpicking appropriate sections of data
      --> Format and scrub DataFrame so that it is ready for machine learning
   
  4. def random_forest_forecast(data)
      --> Chose the random forest regressor model for its powerful prediction capability on short term forecasts
      --> Lacking significant data (merely 3 months worth of stock price history) discouraged implementing other models
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
       --> Uses the same function as def buy() to update target pricing
       --> If position has more than 7.5% loss, the bot orders an immediate sell order on market price
       --> Else, the bot pushes stop/limit order: limit order = target price     stop limit = -7.5% of purchased price
       
    3. if __name__ == '__main__':
       --> Links to Alpaca Paper Trading
       --> Updates Account Status and Positions Held
       --> Run def sell() first to avoid day trading then def buy ()
       --> After pushing orders, the bot will close. 
       --> Task Scheduler will run the script next business day
          
      
