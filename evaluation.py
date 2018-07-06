# -*- encoding:utf-8 -*-
from __future__ import print_function

import csv
import json
import pickle
from datetime import datetime, timedelta
from pathlib import Path

import matplotlib.dates as md
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from textrank4zh import TextRank4Keyword

sns.set(color_codes=True)
sns.set_style("darkgrid")

home = str(Path.home())

with open(home + "/coding/annotation/price0205_0414.json") as data_file:
    price_json = json.load(data_file)

with open(home + "/coding/annotation/processed_chinese_news.pkl", "rb") as data_file:
    processed_news = pickle.load(data_file)

size = len(processed_news)

print("共有2018-02-05至2018-07-05总计" + str(size) + "条新闻，结果会自动保存到result.csv中，标注累了可以开着terminal放在那儿不管，什么时候想回来继续标注了就继续，一旦退出再进来就要从头开始标注")
input("Press Enter to continue...")

with open("result.csv", "w") as csvfile:
    fieldnames = ["id", "influential", "keywords"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

    for index, news in processed_news.iterrows():
        id = news["id"]
        time = news["time"]
        title = news["title"]
        content = news["content"]
        print(time)

        print(index + 1, "/", len(processed_news))
        print("标题：")
        print(title)
        print("摘要：")
        print(content)

        text = "。 ".join([title, content])
        tr4w = TextRank4Keyword()

        tr4w.analyze(text=text, lower=True, window=2)

        print("关键词：")
        machine_keywords = tr4w.get_keywords(10, word_min_len=2)
        for idx, item in enumerate(machine_keywords):
            print(idx, item.word)

        # plot k-line
        df_price = []
        df_price_dict = []
        fig, ax = plt.subplots(figsize=(8, 5))
        time = "2018-04-02 12:45:33"

        time_window = [
            (datetime.strptime(time, "%Y-%m-%d %H:%M:%S") + timedelta(hours=-2)).strftime("%Y-%m-%dT%H:%M:%S"),
            (datetime.strptime(time, "%Y-%m-%d %H:%M:%S") + timedelta(hours=5)).strftime("%Y-%m-%dT%H:%M:%S"),
        ]

        for endpoint in price_json:
            start_time = endpoint["time_period_start"][:19]
            end_time = endpoint["time_period_end"][:19]
            if start_time >= time_window[0] and start_time <= time_window[1] and end_time >= time_window[0] and end_time <= time_window[1]:
                date_time_start = datetime.strptime(endpoint["time_period_start"][:19], "%Y-%m-%dT%H:%M:%S")
                date_time_end = datetime.strptime(endpoint["time_period_end"][:19], "%Y-%m-%dT%H:%M:%S")
                mid_point = date_time_start + timedelta(seconds=30)
                df_tmp = [
                    date_time_start,
                    date_time_end,
                    endpoint["price_close"],
                    endpoint["price_high"],
                    endpoint["price_low"],
                    endpoint["price_open"],
                ]
                df_price.append(df_tmp)
                df_price_dict.append([mid_point, np.mean([endpoint["price_high"], endpoint["price_low"]])])

        df_price_clean = pd.DataFrame(
            df_price, columns=["time_period_start", "time_period_end", "price_close", "price_high", "price_low", "price_open"]
        )
        df_price_dict_df = pd.DataFrame(df_price_dict, columns=["time", "price"])
        df_price_dt = df_price_dict_df.set_index("time").T.to_dict("list")

        for ind, row in df_price_clean.iterrows():
            midpoint = row["time_period_start"] + timedelta(seconds=30)
            plt.plot([midpoint, midpoint], [row["price_low"], row["price_high"]], linewidth=1, color="k")
            if row["price_open"] < row["price_close"]:
                plt.plot([midpoint, midpoint], [row["price_open"], row["price_close"]], linewidth=2, color="r")
            else:
                plt.plot([midpoint, midpoint], [row["price_open"], row["price_close"]], linewidth=2, color="b")

        ax.grid(which="minor")
        hourlocator = md.HourLocator()
        ax.xaxis.set_major_locator(hourlocator)
        ax.xaxis.set_major_formatter(md.DateFormatter("%H:%M"))
        ax.xaxis.set_minor_locator(md.MinuteLocator(byminute=range(0, 60, 10)))
        plt.xlim(min(df_price_clean["time_period_start"]), max(df_price_clean["time_period_end"]))

        lower_bound = min(df_price_clean["price_low"])
        upper_bound = max(df_price_clean["price_high"])

        date_time_marked = datetime.strptime(time, "%Y-%m-%d %H:%M:%S")
        sc = plt.plot([date_time_marked, date_time_marked], [lower_bound, upper_bound], linestyle="--", color="red", linewidth=0.5)

        plt.show(block=False)

        while True:
            is_influential = input("您认为这条新闻是否是一条对价格有影响力的新闻: \n(y: 非常有影响力，n: 非常没有影响力，s: 不确定): ")
            if is_influential == "y" or is_influential == "n" or is_influential == "s":
                break
            else:
                print("请键入y, n, s中的任意一个")

        kws = ""
        if is_influential == "y" or is_influential == "n":
            while True:
                ok = True
                keywords = input("从0到9个关键词中，您认为哪几个关键词决定了您对这条新闻是否有影响力的判断: \n(请给出数字，最多4个，以空格为分隔): ")
                if len(keywords.split()) <= 4 and len(keywords.split()) >= 1:
                    for i in keywords.split():
                        if int(i) < 0 or int(i) > 9:
                            print("请键入0-9的数字，以空格为分隔")
                            ok = False
                            break
                        else:
                            ok = True
                else:
                    print("请键入最多4个数字，最少1个数字，以空格为分隔")
                    ok = False
                if ok:
                    break

            for i in keywords.split():
                kws = " ".join([kws, machine_keywords[int(i)].get("word")])

        writer.writerow({"id": id, "influential": is_influential, "keywords": kws})

        plt.close()

        print("\n")
