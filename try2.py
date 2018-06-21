#-*- encoding:utf-8 -*-
from __future__ import print_function
import codecs
from textrank4zh import TextRank4Keyword, TextRank4Sentence

import sys
try:
    reload(sys)
    sys.setdefaultencoding('utf-8')
except:
    pass

text = "诺贝尔经济学奖获得者Robert J. Shiller：数字货币与其他货币一样。据Finance Magnates消息，诺贝尔经济学奖获得者Robert J. Shiller认为数字货币与其他货币一样，是一个观念的信仰声明，如欧元帮助欧盟成为欧洲人心中的统一体。而BTC与此类似，在一定程度上是一个新世界主义者社区，他们将自己视为高于政府的组织，将政府视为不平等和战争的驱动因素。他认为公众对BTC的迷恋归结为背后的技术，实际上人们迷恋的就是BTC本身。该文章作者对Shiller的观点不予认同。"
tr4w = TextRank4Keyword()

tr4w.analyze(text=text, lower=True, window=2)

print()
print('sentences:')
for s in tr4w.sentences:
    print(s)                 # py2中是unicode类型。py3中是str类型。

print()
print('words_no_filter')
for words in tr4w.words_no_filter:
    print('/'.join(words))   # py2中是unicode类型。py3中是str类型。

print()
print('words_no_stop_words')
for words in tr4w.words_no_stop_words:
    print('/'.join(words))   # py2中是unicode类型。py3中是str类型。

print()
print('words_all_filters')
for words in tr4w.words_all_filters:
    print('/'.join(words))   # py2中是unicode类型。py3中是str类型。