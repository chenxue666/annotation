import json
from datetime import datetime, timedelta

import matplotlib.pyplot as plt
import nltk
import pandas as pd
from rake_nltk import Rake
import requests
import seaborn as sns
# from nltk import ne_chunk, pos_tag
# from nltk.tokenize import word_tokenize
import matplotlib.dates as md
import numpy as np

import nltk; nltk.download('stopwords')

# import RAKE
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

# Get price curve
if os.path.isfile('/Users/chenxue/coding/annotation/price_curve.json'):
    # Read JSON file
    with open('/Users/chenxue/coding/annotation/price_curve.json') as data_file:
        price_json = json.load(data_file)
else:
    url_3 = 'https://rest.coinapi.io/v1/ohlcv/BITSTAMP_SPOT_BTC_USD/history?period_id=1min&time_start=2018-06-06&limit=100000'
    headers = {'X-CoinAPI-Key': 'CB1CD407-B308-4A71-B1B6-B43CEE1B7250'}
    price_response = requests.get(url_3, headers=headers)
    price_json = price_response.json()
    # Write JSON file
    with io.open('/Users/chenxue/coding/annotation/price_curve.json', 'w', encoding='utf8') as outfile:
        str_ = json.dumps(price_json, indent=4, sort_keys=True,
                separators=(',', ': '), ensure_ascii=False)
        outfile.write(to_unicode(str_))

# plot k-line
df_price = []
for endpoint in price_json:
    date_time_start = datetime.strptime(endpoint['time_period_start'][:19], "%Y-%m-%dT%H:%M:%S") 
    date_time_end = datetime.strptime(endpoint['time_period_end'][:19], "%Y-%m-%dT%H:%M:%S") 
    df_tmp = [date_time_start, date_time_end, endpoint["price_close"], endpoint["price_high"], endpoint["price_low"], endpoint["price_open"]]
    df_price.append(df_tmp)

df_price_clean = pd.DataFrame(df_price, columns=['time_period_start', 'time_period_end', 'price_close', 'price_high', 'price_low', 'price_open'])
df_price_20180606 = df_price_clean[df_price_clean['time_period_end'] <= datetime.strptime("2018-06-07T00:00:00", "%Y-%m-%dT%H:%M:%S")]
for ind, row in df_price_20180606.iterrows():
    midpoint = row['time_period_start'] + timedelta(seconds = 30)
    plt.plot([midpoint, midpoint], [row['price_low'], row['price_high']], linewidth=1, color='k')
    if row['price_open'] < row['price_close']:
        plt.plot([midpoint, midpoint], [row['price_open'], row['price_close']], linewidth=4, color='r')
    else:
        plt.plot([midpoint, midpoint], [row['price_open'], row['price_close']], linewidth=4, color='b')

ax=plt.gca()
xfmt = md.DateFormatter('%Y-%m-%d %H:%M:%S')
ax.xaxis.set_major_formatter(xfmt)
plt.xticks(rotation=25)
plt.show()


# Get news
if os.path.isfile('/Users/chenxue/coding/annotation/news.json'):
    # Read JSON file
    with open('/Users/chenxue/coding/annotation/news.json') as data_file:
        res_json = json.load(data_file)
else:
    url = 'https://cryptopanic.com/api/posts/?auth_token=7ad13cff4a303a55ce9c791aa0143a669c6ee1ce&metadata=true&filter=important'
    res = requests.get(url)
    res_json = res.json()
    # Write JSON file
    with io.open('/Users/chenxue/coding/annotation/news.json', 'w', encoding='utf8') as outfile:
        str_ = json.dumps(res_json, indent=4, sort_keys=True,
                separators=(',', ': '), ensure_ascii=False)
        outfile.write(to_unicode(str_))

df = []
# Rake = RAKE.Rake(RAKE.SmartStopList())
r = Rake() # Uses stopwords for english from NLTK, and all puntuation characters.

for news in res_json['results']:   # news['url']
    try:
        desc = news['metadata']['description'].replace('<p>', '').replace('</p>', '').replace('...', '').replace('\n', '').replace('[&#8230;]', '').replace('&nbsp;', '').replace('&#8221;', '').replace('&#160', '').replace('&#8217;', '').replace('&#8220;', '').replace('&#8217;','')
        df_ele = [news['published_at'], ". ".join([news['title'], desc])]
    except:
        df_ele = [news['published_at'], news['title']]
    df.append(df_ele)
    print(df_ele)
    # print("title: %s" % Rake.run(news['title'], maxWords=3))
    # print("tit+des: %s" % Rake.run(df_ele[1], maxWords=3))
    r.extract_keywords_from_text(news['title'])    # df_ele[1]
    r.get_ranked_phrases_with_score() # To get keyword phrases ranked highest to lowest.
    print('\n')

df_clean = pd.DataFrame(df, columns=['date', 'title'])
