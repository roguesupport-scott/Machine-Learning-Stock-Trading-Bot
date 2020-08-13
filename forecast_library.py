import requests
import pandas as pd
import numpy as np
from config import *
from textblob import TextBlob
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor

# Importing StockTwits Data from Automated Stock Alerting Accounts
def importing_twitdata(account1, account2):
    # Importing and Combining Data from 2 Accounts
    r = requests.get(('https://api.stocktwits.com/api/2/streams/user/{}.json').format(account1))
    r2 = requests.get(('https://api.stocktwits.com/api/2/streams/user/{}.json').format(account2))
    twit_data = (r.text + r2.text).split('body')
    # Handpicking Twits that Contain Ticker Names
    for line in twit_data:
        if '$' in line:
            twit_data[twit_data.index(line)] = line.split('created_at')[0].strip('\":\"')
        else:
            twit_data.remove(line)
    return twit_data

# Using Sentiment Analysis to Identify Optimistic Stocks
def twit_sentiment_analyzer(twit_data):
    candidate_list = set()
    for twit_message in twit_data:
        # Sentiment Analysis: 0.4 or Higher Polarity --> Optimistic
        if TextBlob(twit_message).sentiment.polarity > 0.45:
            # Extracting Stock Ticker Name from Clustered Data
            for word in twit_message.split(' '):
                if '$' in word and word[1:] not in candidate_list and '$' not in word[1:] and len(word) in np.arange(2, 6):
                    candidate_list.add(word[1:].upper())
    return candidate_list

# Scrubbing Historical Stock Data: Preparing for Machine Learning Training
def pulling_price_history(ticker):
    # Importing Stock Data and Relevant News Headlines
    stock_price_data = requests.get(('https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={}&apikey='
                                     '{}demo&datatype=csv').format(ticker, ALPHAV_API_KEY)).text.splitlines()[1:]
    news_data = NEWS_API.get_everything(q=(ticker+' stock'), language='en')
    # Organizing Data into pd.DataFrame
    df = pd.DataFrame(pd.DataFrame(stock_price_data)[0].str.split(',', n=6, expand=True))
    df.columns = ['date', 'open', 'high', 'low', 'close', 'volume']
    df['close_price_%change'] = round((df['close'].astype(float) - df['open'].astype(float))
                                       /df['open'].astype(float) * 100, 2)
    # Adding "Press Release" and its "Sentiment Analysis" Data as DataFrame Columns
    headlines = {}
    news_content = list(news_data.values())
    if news_content[1] > 0:
        # Handpicking "News Description" Data within Clustered List and Dict and Storing in "headlines" Dictionary
        for index in range(len(news_content[2])):
            # Identifying "Published Date" within Clustered List/Dict
            date = news_content[2][index]['publishedAt'].split('T')[0]
            headlines[date] = news_content[2][index]['description']
        # Appending News Data to Main DataFrame on Corresponding Dates
        for pr_date in headlines.keys():
            news_analysis = TextBlob(str(headlines[pr_date])).sentiment
            df.loc[df['date'] == pr_date, 'related news'] = 1
            df.loc[df['date'] == pr_date, 'news_polarity'] = news_analysis.polarity
            df.loc[df['date'] == pr_date, 'news_subjectivity'] = news_analysis.subjectivity
    # Data Type Formatting
    df['date'] = pd.to_datetime(df['date'])
    df.set_index('date', inplace=True)
    df[['open', 'high', 'low', 'close', 'volume']] = df[['open', 'high', 'low', 'close', 'volume']].apply(
        pd.to_numeric, errors='coerce')
    df.fillna(0, inplace=True)
    return df

# Forecasting Price with Machine Learning Random Forest Regressor
def random_forest_forecast(data):
    # Training the Model
    X = data.drop(['close'], axis=1)
    y = data['close']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, random_state=101)
    forest = RandomForestRegressor(n_estimators=15)
    forest.fit(X_train, y_train)
    # Substitute of Technical Analysis: (Target Price = Maximum Forecast Price of the Next 20 Business Days * Accuracy Score)
    confidence_level = forest.score(X_test,y_test)
    prediction = round(forest.predict(np.array(X.head(20))).max() * confidence_level, 4)
    return prediction










