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
import time
from bs4 import BeautifulSoup

import RAKE
sns.set(color_codes=True)
sns.set_style("darkgrid")
import os.path
import io

from pathlib import Path
home = str(Path.home())

current_date = "2018-07-24"
filter = "bullish" # important, rising, hot, bullish, bearish

# Get news
if os.path.isfile(home + '/coding/annotation/data/2018_news_'+filter+'.pkl'):
    # Read pickle
    with open(home + '/coding/annotation/data/2018_news_hot.pkl', 'rb') as data_file:
        records_complete = pickle.load(data_file)
else:
    records_complete = []
    page = 1
    while True:
        url = 'https://cryptopanic.com/api/posts/?auth_token=7ad13cff4a303a55ce9c791aa0143a669c6ee1ce&metadata=true&filter='+filter+'&page=' + str(page)  
        print(url)
        page = page + 1
        res_json = requests.get(url).json()
        if max([i['published_at'] for i in res_json['results']]) > current_date:
            break
        else:
            records = res_json['results']
            records_complete.extend(records)
            current_date = min([i['published_at'] for i in res_json['results']])
        time.sleep(1)
    # Write into pickle
    with open(home + '/coding/annotation/data/2018_news_'+filter+'.pkl', 'wb') as data_file:
        pickle.dump(records_complete, data_file)


new_path = home + '/coding/annotation/result/'+filter+'_english_news.txt'
english_news = open(new_path,'w')

Rake = RAKE.Rake(RAKE.SmartStopList())

for news in records_complete:   # news['url']
    try:
        desc = BeautifulSoup(news['metadata']['description'], "html5lib").get_text()
        df_ele = [news['published_at'][:19], news['title'], desc, ". ".join([news['title'], desc])]

        english_news.write("Date:\n %s \n" % df_ele[0])
        english_news.write("Title:\n %s \n" % df_ele[1])
        english_news.write("Description:\n %s" % df_ele[2])
        title_description_kw = Rake.run(df_ele[3], maxWords=2)
        if len(title_description_kw) != 0:
            english_news.write("Keywords:\n %s \n\n" % "\n ".join([i[0] for i in title_description_kw][:10]))
    except:
        df_ele = [news['published_at'][:19], news['title']]

        english_news.write("Date:\n %s \n" % df_ele[0])
        english_news.write("Title:\n %s \n" % df_ele[1])
        title_kw = Rake.run(df_ele[1], maxWords=2)
        if len(title_kw) != 0:
            english_news.write("Keywords:\n %s \n\n" % "\n ".join([i[0] for i in title_kw][:10]))

english_news.close()