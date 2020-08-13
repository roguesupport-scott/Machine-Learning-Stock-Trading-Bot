import pandas as pd
from forecast_library import *

f = open('target_price_list.txt', 'r+')
f_content = f.readlines()
df = pd.DataFrame({'ticker': f_content}).ticker.str.split(expand=True)
target_price = df.loc[df[0] == str("PLM"), 1].astype(float).values[0]

print(target_price)