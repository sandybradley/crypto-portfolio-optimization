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

# all_coins_dict = json.loads(BeautifulSoup(
#         requests.get('https://api.coincap.io/v2/assets').content, "html.parser").prettify())

all_coins_dict = requests.get('https://api.coincap.io/v2/assets').json()
# # print(all_coins_dict)
all_coins_df = pd.DataFrame(all_coins_dict["data"])
# print(all_coins_df)
coins_by_mcap = all_coins_df[all_coins_df["marketCapUsd"].astype(float) > 1e8]
coin_portfolio = coins_by_mcap['id']

save(coin_portfolio,'coin_portfolio')
# coin_portfolio = load('coin_portfolio')

print("Portfolio coins with MCAP > 100 Million :\n",coin_portfolio.values)