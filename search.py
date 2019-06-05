#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jun  1 18:17:05 2019

@author: Adam

@E-mail: shengqiang.liu@videt.cn
"""
import jieba
import math
import operator
import sqlite3
import os
# bm25 confg
from SinaSpyder.bm25_config import *
# 基础配置参数
from config import *

# 数据库地址
db_path = os.path.join(db_dir,db_file_name)
# 创建数据库连接
conn = sqlite3.connect(db_path, check_same_thread=False)

'''检索数据库'''
def fetch_postings_db(term):
    c = conn.cursor()
    c.execute('SELECT * FROM postings WHERE term=?', (term,))
    return (c.fetchone())

'''清洗分词后的文档'''
def clean_list(seg_list):
    cleaned_dict = {}
    n = 0
    for word in seg_list:
        word = word.strip().lower()
        if word != '' and not word.isdigit():
            n += 1
            if word in cleaned_dict:
                cleaned_dict[word] = cleaned_dict[word] + 1
            else:
                cleaned_dict[word] = 1
    return n, cleaned_dict

'''检索答案'''
def fetch_news_db(id):
    c = conn.cursor()
    c.execute('select * from news where id={}'.format(id))
    return (c.fetchone())

'''获取BM25答案'''
def search_use_bm25_model(sentence):
    seg_list = jieba.lcut(sentence)
  
    scores = {}
    
    for word in seg_list:
        dbinfo = fetch_postings_db(word)
        if dbinfo is None:
            continue
        # 所有文档的出现次数
        df = dbinfo[1]
        # idf 权重
        w = math.log2((n - df + 0.5) / (df + 0.5))
        # 出现的文档信息 其id为 所在文档， value为出现次数 length为文档长度
        docs = dbinfo[2].split('\n')

        for doc in docs:
            docid, tf, ld = doc[1:-1].split(',')
            docid = int(docid)
            tf = int(tf)
            ld = int(ld)
            score = (k * tf * w) / (tf + k * (1 - b + b * ld / average))
            if docid in scores:
                scores[docid] += score
            else:
                scores[docid] = score
    scores = sorted(scores.items(), key=operator.itemgetter(1))
    scores.reverse()
    return [fetch_news_db(id) for id,score in scores][:20]

