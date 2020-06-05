import pandas as pd
import numpy as np
import json
from bs4 import BeautifulSoup
import requests
import matplotlib.pyplot as plt

# save data
import pickle 

def save(data,fileName):
    with open(fileName+'.dat', 'wb') as f:
        pickle.dump(data, f)
def load(fileName):
    with open(fileName+'.dat', 'rb') as f:
        new_data = pickle.load(f)
        return new_data

# # all_coins_dict = json.loads(BeautifulSoup(
# #         requests.get('https://api.coincap.io/v2/assets').content, "html.parser").prettify())

# all_coins_dict = requests.get('https://api.coincap.io/v2/assets').json()
# # # print(all_coins_dict)
# all_coins_df = pd.DataFrame(all_coins_dict["data"])
# # print(all_coins_df)
# coins_by_mcap = all_coins_df[all_coins_df["marketCapUsd"].astype(float) > 1e8]
# coin_portfolio = coins_by_mcap['id']

# save(coin_portfolio,'coin_portfolio')
coin_portfolio = load('coin_portfolio')

#Create a DataFrame that will hold all the price & data for all the selected coins
combined_df = pd.DataFrame()
# combined_df = load('combined_df')

#Loop thru all the coins in the portfolio & get their historical prices. (180 days)
for coin in coin_portfolio:
# for coin in new_coins:
    dic_t = requests.get('https://api.coincap.io/v2/assets/'+coin+'/history?interval=d1').json()
    # print(dic_t)
    dic_df = pd.DataFrame(dic_t["data"])
    # print(dic_df)
    prices = dic_df.get(['priceUsd','date'])
    # print(prices)
    coindf = prices.copy()
    # coindf = pd.DataFrame.from_records(prices,columns=['time','price'])
    coindf['coin'] = coin
    print(coindf)
    combined_df = combined_df.append(coindf, ignore_index=True)

save(combined_df,'combined_df')

combined_df['priceUsd'] = combined_df['priceUsd'].astype(float)

# #Change the time formart
# combined_df['time'] = pd.to_datetime(combined_df['time'],unit='ms')
# combined_df['time'] = [d.date() for d in combined_df['time']]

operational_df = combined_df.groupby(['date', 'coin'],as_index=False)[['priceUsd']].mean()
operational_df = operational_df.set_index('date')
# print(operational_df.iloc[[0, -1]])
pivoted_portfolio = operational_df.pivot(columns='coin')

pivoted_portfolio.to_csv('crypto_prices.csv', index=False)

daily_returns = pivoted_portfolio.pct_change()
daily_returns_cumsum = np.exp(np.log1p(daily_returns).cumsum())-1

daily_returns_cumsum.to_csv('asset_retruns.csv', index=False)