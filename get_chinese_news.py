import requests
import pickle

import os.path
import pandas as pd
from hashlib import md5
from bs4 import BeautifulSoup

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


# process chinese news
if os.path.isfile(home + '/coding/annotation/processed_chinese_new.pkl'):
    # Read pickle
    with open(home + '/coding/annotation/processed_chinese_news.pkl', 'rb') as data_file_2:
        processed_chinese_news = pickle.load(data_file_2)
else:
    df_ele = []
    for news in records_complete:
        title = news['title']
        # Remove HTML tags using Beautiful Soup library
        content = BeautifulSoup(news['content'], "html5lib").get_text()
        time_at = news['updateTime']
        id = md5(title.encode('utf-8')).hexdigest()
        df_ele.append([id, time_at, title, content])

    df = pd.DataFrame(df_ele, columns=['id', 'time', 'title', 'content'])
    # Write into pickle
    with open(home + '/coding/annotation/processed_chinese_news.pkl', 'wb') as data_file_2:
        pickle.dump(df, data_file_2)


# # jinse
# jinsestr = "https://api.jinse.com/topic/list"
# s = "access_key=d4b0fa5b6ab53fac6433e6479451e19f&date="+str(int(time.time()))+"&last_id=20000&"
# s_sign = s + "secret_key=c5ef763442c1a510"
# sign = md5(s_sign.encode('utf-8')).hexdigest()
# url = jinsestr + "?" + s + "sign=" + sign
# print(url)

# if os.path.isfile(home + '/coding/annotation/jinse_chinese_news.pkl'):
#     # Read pickle
#     with open(home + '/coding/annotation/jinse_chinese_news.pkl', 'rb') as data_file:
#         records_complete = pickle.load(data_file)
# else:
#     records_complete = []
#     page = 1
#     while page <= 100:
#         url = 'https://api.apishop.net/common/coin/searchNews?apiKey=SeiykRj6e0d0ccc2e6011e45e785523e5f583d2a5cd1550&keyword=BTC&page=' + str(page)  # important, rising, hot, bullish, bearish
#         print(url)
#         page = page + 1
#         res = requests.get(url)
#         res_json = res.json()
#         records = res_json['result']['newsList']
#         records_complete.extend(records)
#     # Write into pickle
#     with open(home + '/coding/annotation/chinese_news.pkl', 'wb') as data_file:
#         pickle.dump(records_complete, data_file)