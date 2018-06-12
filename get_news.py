import json
from datetime import datetime

import matplotlib.pyplot as plt
import nltk
import pandas as pd
import RAKE
import requests
import seaborn as sns
from nltk import ne_chunk, pos_tag
from nltk.tokenize import word_tokenize

nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('maxent_ne_chunker')
nltk.download('words')
sns.set(color_codes=True)
sns.set_style("darkgrid")
import os.path
import io

try:
    to_unicode = unicode
except NameError:
    to_unicode = str

# Get price curve
if os.path.isfile('/Users/xuechen/news_annotation/price_curve.json'):
    # Read JSON file
    with open('/Users/xuechen/news_annotation/price_curve.json') as data_file:
        response_json = json.load(data_file)
else:
    url_3 = 'https://rest.coinapi.io/v1/ohlcv/BITSTAMP_SPOT_BTC_USD/history?period_id=&time_start=2018-06-06&limit=100000'
    headers = {'X-CoinAPI-Key': '8555DCE6-978F-458F-AEC2-2F930CDA5594'}
    response = requests.get(url_3, headers=headers)
    response_json = response.json()
    # Write JSON file
    with io.open('/Users/xuechen/news_annotation/price_curve.json', 'w', encoding='utf8') as outfile:
        str_ = json.dumps(response_json, indent=4, sort_keys=True,
                separators=(',', ': '), ensure_ascii=False)
        outfile.write(to_unicode(str_))

df_price = []
for endpoint in response_json:
    date = datetime.strptime(endpoint['time_period_start'], "%Y-%m-%d")
    df_tmp = [date.date(), endpoint['price_open']]
    df_price.append(df_tmp)
    print(df_tmp)
    print('\n')

df_price_clean = pd.DataFrame(df_price, columns=['date', 'price_open'])
plt.plot(df_price_clean['date'], df_price_clean['price_open'])
plt.show()

# Get news
if os.path.isfile('/Users/xuechen/news_annotation/news.json'):
    # Read JSON file
    with open('/Users/xuechen/news_annotation/news.json') as data_file:
        res_json = json.load(data_file)
else:
    url = 'https://cryptopanic.com/api/posts/?auth_token=7ad13cff4a303a55ce9c791aa0143a669c6ee1ce&metadata=true&filter=important'
    res = requests.get(url)
    res_json = res.json()
    # Write JSON file
    with io.open('/Users/xuechen/news_annotation/news.json', 'w', encoding='utf8') as outfile:
        str_ = json.dumps(res_json, indent=4, sort_keys=True,
                separators=(',', ': '), ensure_ascii=False)
        outfile.write(to_unicode(str_))

df = []
Rake = RAKE.Rake(RAKE.SmartStopList())

for news in res_json['results']:   # news['url']
    try:
        desc = news['metadata']['description'].replace('<p>', '').replace('</p>', '').replace('...', '').replace('\n', '').replace('[&#8230;]', '').replace('&nbsp;', '').replace('&#8221;', '').replace('&#160', '').replace('&#8217;', '').replace('&#8220;', '').replace('&#8217;','')
        df_ele = [news['published_at'], ". ".join([news['title'], desc])]
    except:
        df_ele = [news['published_at'], news['title']]
    df.append(df_ele)
    print(df_ele)
    print("title: %s" % Rake.run(news['title'], maxWords=3))
    print("tit+des: %s" % Rake.run(df_ele[1], maxWords=3))
    print('\n')

df_clean = pd.DataFrame(df, columns=['date', 'title'])
