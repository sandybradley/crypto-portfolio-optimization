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


pivoted_portfolio = pd.read_csv("crypto_prices_sub.csv") 
# get covariance & returns of the coin - daily & for the period 
daily_returns = pivoted_portfolio.pct_change()
# daily_returns_sum = daily_returns.sum()
# daily_returns_cumsum = np.exp(np.log1p(daily_returns).cumsum())-1
# daily_cor = daily_returns.corr()
# daily_cor_sub = daily_cor[daily_cor < 0.5]
# print(daily_cor_sub)
# figure = ff.create_annotated_heatmap(
#     z=corrs.values,
#     x=list(corrs.columns),
#     y=list(corrs.index),
#     annotation_text=corrs.round(2).values,
#     showscale=True)
# plt.matshow(daily_cor)
# plt.show()
# print(daily_cor.info())
# print(daily_cor.loc['priceUsd','bitcoin'].sort_values(ascending=True))
# daily_returns_cumsum.to_csv('file_name.csv', index=False)
# daily_cor.to_csv('bitcoincorrelations.csv', index=False)
# pivoted_portfolio.to_csv('crypto_prices.csv', index=False)
# print(daily_returns_cumsum.iloc[-1].sort_values(ascending=False))

# period_returns = daily_returns.mean()*729

# daily_covariance = daily_returns.cov()
# period_covariance = daily_covariance*729

p_returns, p_volatility, p_sharpe_ratio, p_coin_weights=([] for i in range(4))

# portfolio combinations to probe
number_of_cryptoassets = len(daily_returns.columns)
number_crypto_portfolios = 10000

# for each portoflio, get returns, risk and weights
for a_crypto_portfolio in range(number_crypto_portfolios):
    weights = np.random.random(number_of_cryptoassets)
    weights /= np.sum(weights)
    
    # print(weights)
    cumsum = []
    cumsum.append( 100.0)

    for index, row in daily_returns.iterrows():
        # print(index)
        if index > 0:
            returnsPort = np.dot(weights, row)
            # print(returnsPort)
            portValue = cumsum[index-1] + (cumsum[index-1] * returnsPort)
            # print(cumsum[index-1],portValue)
            cumsum.append(portValue)

    # returns = np.dot(weights, period_returns)*100
    returns = 100 * (cumsum[-1] - cumsum[0])/cumsum[0]
    # print(returns)
    # print(cumsum)
    cumsum = pd.Series(cumsum)
    cumsumReturns = cumsum.pct_change()
    # print(cumsumReturns)
    # volatility = np.sqrt(np.dot(weights.T, np.dot(period_covariance, weights)))*100
    # daily_covariance = cumsumReturns.cov()
    # period_covariance = daily_covariance * len(cumsumReturns)
    # volatility = np.sqrt(np.dot(weights.T, np.dot(period_covariance, weights)))*100
    volatility = 100 * cumsumReturns.std()
   
    p_sharpe_ratio.append(returns/volatility)
    p_returns.append(returns)
    p_volatility.append(volatility)
    p_coin_weights.append(weights)

# a dictionary for Returns and Risk values of each portfolio
portfolio = {'volatility': p_volatility,
             'sharpe_ratio': p_sharpe_ratio, 'returns': p_returns}

# extend original dictionary to accomodate each ticker and weight in the portfolio
for counter,symbol in enumerate(daily_returns.columns):
    portfolio[symbol+'-%'] = [Weight[counter] for Weight in p_coin_weights]

# make a nice dataframe of the extended dictionary
df = pd.DataFrame(portfolio)

order_cols = ['returns', 'volatility', 'sharpe_ratio']+[coin+'-%' for coin in daily_returns.columns]
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
print("Best Sharpe")
print(sharpe_portfolio.T)
print("Min Volatility")
print(min_variance_port.T)
print("Max Returns")
print(max_returns_port.T)