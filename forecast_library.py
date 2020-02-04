import requests
import pandas as pd
import numpy as np
from config import *
from textblob import TextBlob
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor


# Importing StockTwits Data from Automated Stock Alerting Accounts
def importing_twitdata(id1, id2):
    # Importing and Combining Data from 2 Accounts
    r = requests.get('https://api.stocktwits.com/api/2/streams/user/'+id1+'.json')
    r2 = requests.get('https://api.stocktwits.com/api/2/streams/user/'+id2+'.json')
    twit_data = (r.text + r2.text).split('body')
    # Handpicking Twits that Refer Stock Tickers
    for line in twit_data:
        if '$' in line:
            twit_data[twit_data.index(line)] = line.split('created_at')[0].strip('\":\"')
        else:
            twit_data.remove(line)
    return twit_data


# Using Sentiment Analysis to Identify Optimistic Stocks
def twit_sentiment_analyzer(raw_data):
    candidate_list = []
    for twit_message in raw_data:
        # Identifying Optimistic Twits
        if TextBlob(twit_message).sentiment.polarity > 0.4:
            # Extracting Stock Ticker Name from Clustered Data
            for ticker in twit_message.split(' '):
                if '$' in ticker and ticker[1:] not in candidate_list and len(ticker) in np.arange(3,6):
                    candidate_list.append(ticker[1:].upper())
    return candidate_list


# Scrubbing Historical Stock Data: Readily Use for Machine Learning
def stock_price_history(ticker):
    # Importing Stock Data and Relevant News Headlines
    stock_price_data = requests.get('https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol='+ticker+'&apikey='+ALPHAV_API_KEY+'demo&datatype=csv').text.splitlines()[1:]
    news_data = NEWS_API.get_everything(q=(ticker+' stock'), language='en')

    # Organizing Data into pd.DataFrame
    df = pd.DataFrame(pd.DataFrame(stock_price_data)[0].str.split(',', n=6, expand=True))
    df.columns = ['date', 'open', 'high', 'low', 'close', 'volume']
    df['close_price_change_%'] = round((df['close'].astype(float) - df['open'].astype(float))/df['open'].astype(float) * 100, 2)

    # Adding "Press Release" and "Sentiment Analysis" Data as Columns in the DataFrame
    headlines = {}
    news_content = list(news_data.values())
    if news_content[1] > 0:
        # Handpicking "News Description" Data within Clustered List and Dict
        for i in np.arange(len(news_content[2])):
            # Identifying "Published Date" within Clustered List/Dict
            date = news_content[2][i]['publishedAt'].split('T')[0]
            headlines[date] = news_content[2][i]['description']
        # Appending News Data to Main DataFrame on Corresponding Dates
        for key in headlines.keys():
            df.loc[df['date'] == key, 'related news'] = 1
            df.loc[df['date'] == key, 'news_sentiment'] = TextBlob(headlines[key]).sentiment.polarity
            df.loc[df['date'] == key, 'news_subjectivity'] = TextBlob(headlines[key]).sentiment.subjectivity

    # Data Type Formatting
    df['date'] = pd.to_datetime(df['date'])
    df.set_index('date', inplace=True)
    df[['open', 'high', 'low', 'close', 'volume']] = df[['open', 'high', 'low', 'close', 'volume']].apply(pd.to_numeric, errors='coerce')
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

    # Technical Analysis: (Target Price = Maximum Forecast Price of the Next 20 Business Days * Accuracy Score)
    confidence_level = forest.score(X_test,y_test)
    prediction = round(forest.predict(np.array(X.head(20))).max() * confidence_level,4)
    return prediction










