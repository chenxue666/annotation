import requests
import pickle

import os.path
import io

from pathlib import Path
home = str(Path.home())

if os.path.isfile(home + '/coding/annotation/chinese_news.pkl'):
    # Read pickle
    with open(home + '/coding/annotation/chinese_news.pkl', 'rb') as data_file:
        records_complete = pickle.load(data_file)
else:
    records_complete = []
    page = 1
    while page <= 100:
        url = 'https://api.apishop.net/common/coin/searchNews?apiKey=SeiykRj6e0d0ccc2e6011e45e785523e5f583d2a5cd1550&keyword=BTC&page=' + str(page)  # important, rising, hot, bullish, bearish
        print(url)
        page = page + 1
        res = requests.get(url)
        res_json = res.json()
        records = res_json['result']['newsList']
        records_complete.extend(records)
    # Write into pickle
    with open(home + '/coding/annotation/chinese_news.pkl', 'wb') as data_file:
        pickle.dump(records_complete, data_file)

for news in records_complete:
    title = news['title']
    content = news['content']
    time = news['updateTime']
    df_ele = [time, title, content, ". ".join([title, content])]
    print("-Title: %s" % df_ele[1])
    print("-Description: %s" % df_ele[2])

