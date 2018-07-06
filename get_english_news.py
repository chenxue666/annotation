import json
from datetime import datetime, timedelta

import matplotlib.pyplot as plt
import nltk
import pandas as pd
from rake_nltk import Rake
import requests
import seaborn as sns
from nltk import ne_chunk, pos_tag
from nltk.tokenize import word_tokenize
import matplotlib.dates as md
import numpy as np
import pickle

import RAKE
# nltk.download('punkt')
# nltk.download('averaged_perceptron_tagger')
# nltk.download('maxent_ne_chunker')
# nltk.download('words')
sns.set(color_codes=True)
sns.set_style("darkgrid")
import os.path
import io

try:
    to_unicode = unicode
except NameError:
    to_unicode = str

from pathlib import Path
home = str(Path.home())

##########
### run 3 parts, and then combine them

# start_date = "2018-02-05"
# end_date = "2018-04-14"

# # start_date = "2018-04-15"
# # end_date = "2018-06-14"

# # start_date = "2018-06-15"
# # end_date = "2018-07-06"

# # next_date = (datetime.strptime(current_date, "%Y-%m-%d") + timedelta(days=1)).strftime("%Y-%m-%d")

# # Get price curve
# if os.path.isfile(home + '/coding/annotation/price_234.json'):
#     # Read JSON file
#     with open(home + '/coding/annotation/price_234.json') as data_file:
#         price_json = json.load(data_file)
# else:
#     url_3 = 'https://rest.coinapi.io/v1/ohlcv/BITSTAMP_SPOT_BTC_USD/history?period_id=1min&time_start='+start_date+'&time_end='+end_date+'&limit=100000'
#     headers = {'X-CoinAPI-Key': 'BE597240-9259-4526-A8EB-E0E46E1B828D'}
#     price_response = requests.get(url_3, headers=headers)
#     price_json = price_response.json()
#     # Write JSON file
#     with io.open(home + '/coding/annotation/price_234.json', 'w', encoding='utf8') as outfile:
#         str_ = json.dumps(price_json, indent=4, sort_keys=True,
#                 separators=(',', ': '), ensure_ascii=False)
#         outfile.write(to_unicode(str_))

##########

current_date = "2018-06-17"
next_date = (datetime.strptime(current_date, "%Y-%m-%d") + timedelta(days=1)).strftime("%Y-%m-%d")

# Get price curve
if os.path.isfile(home + '/coding/annotation/price_curve.json'):
    # Read JSON file
    with open(home + '/coding/annotation/price_curve.json') as data_file:
        price_json = json.load(data_file)
else:
    url_3 = 'https://rest.coinapi.io/v1/ohlcv/BITSTAMP_SPOT_BTC_USD/history?period_id=1min&time_start='+current_date+'&time_end='+next_date+'&limit=10000'
    headers = {'X-CoinAPI-Key': 'BE597240-9259-4526-A8EB-E0E46E1B828D'}
    price_response = requests.get(url_3, headers=headers)
    price_json = price_response.json()
    # Write JSON file
    with io.open(home + '/coding/annotation/price_curve.json', 'w', encoding='utf8') as outfile:
        str_ = json.dumps(price_json, indent=4, sort_keys=True,
                separators=(',', ': '), ensure_ascii=False)
        outfile.write(to_unicode(str_))

# plot k-line
df_price = []
df_price_dict = []
fig, ax = plt.subplots(figsize=(8, 5))

for endpoint in price_json:
    date_time_start = datetime.strptime(endpoint['time_period_start'][:19], "%Y-%m-%dT%H:%M:%S") 
    date_time_end = datetime.strptime(endpoint['time_period_end'][:19], "%Y-%m-%dT%H:%M:%S") 
    mid_point = date_time_start + timedelta(seconds = 30)
    df_tmp = [date_time_start, date_time_end, endpoint["price_close"], endpoint["price_high"], endpoint["price_low"], endpoint["price_open"]]
    df_price.append(df_tmp)
    df_price_dict.append([mid_point, np.mean([endpoint["price_high"], endpoint["price_low"]])])

df_price_clean = pd.DataFrame(df_price, columns=['time_period_start', 'time_period_end', 'price_close', 'price_high', 'price_low', 'price_open'])
df_price_dict_df = pd.DataFrame(df_price_dict, columns=['time', 'price'])
df_price_dt = df_price_dict_df.set_index('time').T.to_dict('list')

for ind, row in df_price_clean.iterrows():
    midpoint = row['time_period_start'] + timedelta(seconds = 30)
    plt.plot([midpoint, midpoint], [row['price_low'], row['price_high']], linewidth=1, color='k')
    if row['price_open'] < row['price_close']:
        plt.plot([midpoint, midpoint], [row['price_open'], row['price_close']], linewidth=2, color='r')
    else:
        plt.plot([midpoint, midpoint], [row['price_open'], row['price_close']], linewidth=2, color='b')

ax.set(title=current_date)
ax.grid(which='minor')
hourlocator = md.HourLocator()
ax.xaxis.set_major_locator(hourlocator)
ax.xaxis.set_major_formatter(md.DateFormatter("%H:%M"))
ax.xaxis.set_minor_locator(md.MinuteLocator(byminute=range(0, 60, 10)))
plt.xlim(min(df_price_clean['time_period_start']), max(df_price_clean['time_period_end']))


# Get news
if os.path.isfile(home + '/coding/annotation/news_hot.pkl'):
    # Read pickle
    with open(home + '/coding/annotation/news_hot.pkl', 'rb') as data_file:
        records_complete = pickle.load(data_file)
else:
    records_complete = []
    page = 1
    while True:
        url = 'https://cryptopanic.com/api/posts/?auth_token=7ad13cff4a303a55ce9c791aa0143a669c6ee1ce&metadata=true&filter=hot&page=' + str(page)  # important, rising, hot, bullish, bearish
        print(url)
        page = page + 1
        res = requests.get(url)
        res_json = res.json()
        if min([i['published_at'][:10] for i in res_json['results']]) > current_date:
            continue
        elif max([i['published_at'][:10] for i in res_json['results']]) < current_date:
            break
        else:
            records = [record for record in res_json['results'] if record['published_at'][:10]==current_date]
            records_complete.extend(records)
    # Write into pickle
    with open(home + '/coding/annotation/news.pkl', 'wb') as data_file:
        pickle.dump(records_complete, data_file)

df = []
Rake = RAKE.Rake(RAKE.SmartStopList())

lower_bound = min(df_price_clean['price_low'])
upper_bound = max(df_price_clean['price_high'])
news_date_kw = []

for news in records_complete:   # news['url']
    try:
        desc = news['metadata']['description'].replace('<p>', '').replace('</p>', '').replace('...', '').replace('\n', '').replace('[&#8230;]', '').replace('&nbsp;', '').replace('&#8221;', '').replace('&#160', '').replace('&#8217;', '').replace('&#8220;', '').replace('&#8217;','')
        df_ele = [news['published_at'][:19], news['title'], desc, ". ".join([news['title'], desc])]
        print("-Title: %s" % df_ele[1])
        print("-Description: %s" % df_ele[2])
        title_kw = Rake.run(df_ele[1], maxWords=2)
        if len(title_kw) != 0:
            print("-Keywords from title: %s" % title_kw[0][0])
        else:
            print("-Keywords from title: []")
        description_kw = Rake.run(df_ele[2], maxWords=2)
        if len(description_kw) != 0:
            print("-Keywords from description: %s" % description_kw[0][0])
        else:
            print("-Keywords from description: []")
        title_description_kw = Rake.run(df_ele[3], maxWords=2)
        if len(title_description_kw) != 0:
            print("-Keywords from title & description: %s" % title_description_kw[0][0])
            kw = title_description_kw[0][0]
        else:
            print("-Keywords from title & description: []")
            kw = []
        print('\n')
    except:
        df_ele = [news['published_at'][:19], news['title']]
        print("-Title: %s" % df_ele[1])
        title_kw = Rake.run(df_ele[1], maxWords=2)
        if len(title_kw) != 0:
            print("-Keywords from title: %s" % title_kw[0][0])
            kw = title_kw[0][0]
        else:
            print("-Keywords from title: []")
            kw = []
        print('\n')
    # df.append(df_ele)
    date_time_marked = datetime.strptime(news['published_at'][:19], "%Y-%m-%dT%H:%M:%S")
    news_date_kw.append([date_time_marked, kw])
    sc = plt.plot([date_time_marked, date_time_marked], [lower_bound, upper_bound], linestyle="--", color="red", linewidth=0.5)

news_date_keywords = pd.DataFrame(news_date_kw, columns=["date", "kw"])
y = [df_price_dt[min(key for key in df_price_dt.keys() if key >= date)][0] for date in news_date_keywords['date']]
sc = plt.scatter(news_date_keywords['date'].tolist(), y, color="red")

for i in range(len(news_date_keywords)):
    if len(news_date_keywords['kw'][i]) != 0:
        annot = ax.annotate(news_date_keywords['kw'][i], xy=(md.date2num(news_date_keywords['date'][i]), y[i]),
                    xycoords='data',
                    xytext=(10, -40),
                    textcoords="offset points",
                    bbox=dict(boxstyle="round4,pad=.5", fc="0.9"),
                    arrowprops=dict(arrowstyle="->",
                                connectionstyle="arc3,rad=-0.2"))

# df_clean = pd.DataFrame(df, columns=['date', 'title'])

plt.show()
