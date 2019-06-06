#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jun  1 17:31:50 2019

@author: Adam

@E-mail: shengqiang.liu@videt.cn
"""
import sqlite3
from flask import Flask, request, render_template, url_for,redirect
from search import search_use_bm25_model
from search import conn
from search import init_history_db
from search import update_history
from config import label_list
app = Flask(__name__)


@app.route("/")
def root():
    '''
    主页面
    ''' 
    news = []
    try:
        c = conn.cursor()
        c.execute('select id,title from news limit 10')
        news = c.fetchall()
    except Exception as e:
        print("hots news error:", e)

    history = []
    try:
        c.execute('''select a.id,a.title
                            from news as a  inner join
                            (select id from history ORDER BY times limit 10) as b
                            on  a.id=b.id''')
        history = c.fetchall()
    except Exception as e:
        print("history news error:", e)

    return render_template("Index.html", hots=news, history=history)

@app.route("/search", methods=['POST', 'GET'])
def search():
    """
    新闻检索
    :return: Search.html
    """
    docs = []
    result = {label: [] for label in label_list}
    keyword = ''
    try:
        if request.method == 'GET':
            keyword = request.values.get('keyword')
            keyword = keyword.strip()
            if keyword:
                docs = search_use_bm25_model(keyword)
                for doc in docs:
                    for label in label_list:
                        if doc[1] == label:
                            result[label].append(doc)
    except Exception as e:
        print('search engine error:',e)
    if docs:
        return render_template("Search.html",
                                 docs = docs,
                                 result = result,
                                 key = keyword
                                 )     
    else:
        return redirect(url_for('root'))


@app.route("/news", methods=['POST', 'GET'])
def newsinfo():
    """
    书籍详情
    :return: news.html
    """
    init_history_db()

    news = []
    recommend_news = []
    try:
        if request.method == 'GET':
            newsid = request.args.get('newsid')

            update_history(newsid)

            c = conn.cursor()
            c.execute('select * from news where id= {} '.format(newsid))
            news = c.fetchone()

            c.execute('select * from recommend where id={}'.format(newsid))
            recommends = c.fetchone()

            recommends = recommends[1:]
            recommend_news = []
            for recommend_id in recommends :
                c.execute('select id,title from news where id={}'.format(recommend_id))
                recommend_news.append(c.fetchone())


    except Exception as e:
        print('news info error:',e)

    return render_template('News.html',doc=news, recommends=recommend_news)

if __name__ == '__main__':
    app.run(debug=True, port=8080)