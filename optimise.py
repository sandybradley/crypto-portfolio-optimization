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
# # print(all_coins_dict)
# all_coins_df = pd.DataFrame(all_coins_dict["data"])
# # print(all_coins_df)
# coins_by_mcap = all_coins_df[all_coins_df["marketCapUsd"].astype(float) > 1e9]
# coin_portfolio = coins_by_mcap['id']

# save(coin_portfolio,'coin_portfolio')
coin_portfolio = load('coin_portfolio')
# del(coin_portfolio['bitcoin-sv'])
# del(coin_portfolio['ethereum'])
# coin_portfolio.drop([,'ethereum'])

# indexVal = coin_portfolio[ coin_portfolio.values == 'bitcoin-sv' ].index
# coin_portfolio.drop(indexVal , inplace=True)
# indexVal = coin_portfolio[ coin_portfolio.values == 'ethereum' ].index
# coin_portfolio.drop(indexVal , inplace=True)
# indexVal = coin_portfolio[ coin_portfolio.values == 'nano' ].index
# coin_portfolio.drop(indexVal , inplace=True)
# indexVal = coin_portfolio[ coin_portfolio.values == 'zcash' ].index
# coin_portfolio.drop(indexVal , inplace=True)
# new_coins = pd.Series(['zcash'])
# not enough data on this api for nano
# coin_portfolio.append(new_coins)
print("Portfolio coins with MCAP > 1 Billion :\n",coin_portfolio.values)
# save(coin_portfolio,'coin_portfolio')

#Create a DataFrame that will hold all the price & data for all the selected coins
combined_df = pd.DataFrame()
combined_df = load('combined_df')
# indexVal = combined_df[ combined_df["coin"] == 'bitcoin-sv' ].index
# combined_df.drop(indexVal , inplace=True)
# indexVal = combined_df[ combined_df["coin"] == 'ethereum' ].index
# combined_df.drop(indexVal , inplace=True)
# #Loop thru all the coins in the portfolio & get their historical prices. (180 days)
# for coin in coin_portfolio:
# for coin in new_coins:
#     dic_t = requests.get('https://api.coincap.io/v2/assets/'+coin+'/history?interval=d1').json()
#     # print(dic_t)
#     dic_df = pd.DataFrame(dic_t["data"])
#     # print(dic_df)
#     prices = dic_df.get(['priceUsd','date'])
#     # print(prices)
#     coindf = prices.copy()
#     # coindf = pd.DataFrame.from_records(prices,columns=['time','price'])
#     coindf['coin'] = coin
#     print(coindf)
#     combined_df = combined_df.append(coindf, ignore_index=True)

# save(combined_df,'combined_df')

combined_df['priceUsd'] = combined_df['priceUsd'].astype(float)
# #Change the time formart
# combined_df['time'] = pd.to_datetime(combined_df['time'],unit='ms')
# combined_df['time'] = [d.date() for d in combined_df['time']]

operational_df = combined_df.groupby(['date', 'coin'],as_index=False)[['priceUsd']].mean()
operational_df = operational_df.set_index('date')
print(operational_df.iloc[[0, -1]])
pivoted_portfolio = operational_df.pivot(columns='coin')

# get covariance & returns of the coin - daily & for the period 

daily_returns = pivoted_portfolio.pct_change()
period_returns = daily_returns.mean()*720

daily_covariance = daily_returns.cov()
period_covariance = daily_covariance*720

p_returns, p_volatility, p_sharpe_ratio, p_coin_weights=([] for i in range(4))

# portfolio combinations to probe
number_of_cryptoassets = len(coin_portfolio)
number_crypto_portfolios = 50000

# for each portoflio, get returns, risk and weights
for a_crypto_portfolio in range(number_crypto_portfolios):
    weights = np.random.random(number_of_cryptoassets)
    weights /= np.sum(weights)
    
    #print(weights)
    returns = np.dot(weights, period_returns)*100
    
    #print(weights)
    volatility = np.sqrt(np.dot(weights.T, np.dot(period_covariance, weights)))*100
   
    p_sharpe_ratio.append(returns/volatility)
    p_returns.append(returns)
    p_volatility.append(volatility)
    p_coin_weights.append(weights)

# a dictionary for Returns and Risk values of each portfolio
portfolio = {'volatility': p_volatility,
             'sharpe_ratio': p_sharpe_ratio, 'returns': p_returns}

# extend original dictionary to accomodate each ticker and weight in the portfolio
for counter,symbol in enumerate(coin_portfolio):
    portfolio[symbol+'-%'] = [Weight[counter] for Weight in p_coin_weights]

# make a nice dataframe of the extended dictionary
df = pd.DataFrame(portfolio)

order_cols = ['returns', 'volatility', 'sharpe_ratio']+[coin+'-%' for coin in coin_portfolio]
df = df[order_cols]

sharpe_portfolio = df.loc[df['sharpe_ratio'] == df['sharpe_ratio'].max()]
min_variance_port = df.loc[df['volatility'] == df['volatility'].min()]
max_returns_port = df.loc[df['returns'] == df['returns'].max()]

plt.style.use('seaborn-dark')
df.plot.scatter(x='volatility', y='returns', c='sharpe_ratio', cmap='PRGn_r', 
                edgecolors='black', figsize=(10, 7), grid=True)

plt.xlabel('Volatility (Std. Deviation)')
plt.ylabel('Expected Returns')
plt.title('Efficient Frontier')
plt.show()

print('****Portfolio llocations*****')
print(sharpe_portfolio.T)
