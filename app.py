#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jun  1 17:31:50 2019

@author: Adam

@E-mail: shengqiang.liu@videt.cn
"""
import sqlite3
from flask import Flask, request, render_template
from search import search_use_bm25_model
from search import conn

app = Flask(__name__)

label_list = ["news", "sports", "fashion", "finance", "ent", "tech", 
              "edu", "travel", "games", "auto"]

@app.route("/")
def root():
    '''
    主页面
    ''' 
    return render_template("Index.html")

@app.route("/search", methods=['POST', 'GET'])
def search():
    """
    新闻检索
    :return: Search.html
    """
    result = {'news' : [],
            'sports' : [],
            'fashion' : [],
            'finance' : [],
            'ent' : [],
            'tech' : [],
            'edu' : [],
            'travel' : [],
            'games' : [],
            'auto' : [] }
    try:
        if request.method == 'GET':
            keyword = request.values.get('keyword')
            keyword = keyword.strip()
            docs = search_use_bm25_model(keyword)
            for doc in docs:
                for label in label_list:
                    if doc[1] == label:
                        result[label].append(doc)
    except:
        docs = []
    return render_template("Search.html",
                             docs = docs,
                             result = result,
                             key = keyword
                             )        

@app.route("/news", methods=['POST', 'GET'])
def newsinfo():
    """
    书籍详情
    :return: news.html
    """
    news = []
    recommend = []
    if request.method == 'GET':
        newsid = request.args.get('newsid')

        c = conn.cursor()
        c.execute('select * from news where id= {} '.format(newsid))
        news = c.fetchone()

        c.execute('select * from recommend where id={}'.format(newsid))
        recommends = c.fetchone()
        recommend_news = []
        for recommend_id in recommends:
            c.execute('select id,title from news where id={}'.format(recommend_id))
            recommend_news.append(c.fetchone())
        
        print(recommend_news)
    return render_template('News.html',doc=news, recommends=recommend_news)

if __name__ == '__main__':
    app.run(debug=True, port=8080)