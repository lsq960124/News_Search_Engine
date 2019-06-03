#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jun  1 14:58:34 2019

@author: Adam

@E-mail: shengqiang.liu@videt.cn
"""
import threading
import multiprocessing
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import sqlite3

conn = sqlite3.connect('./db/ir.db')
c = conn.cursor()
c.execute('''DROP TABLE IF EXISTS news''')
c.execute('''CREATE TABLE news
             (id INTEGER PRIMARY KEY, label TEXT, url TEXT, title TEXT , dt TEXT, article TEXT)''')
conn.commit()
conn.close()

with open("./data/links.txt","r") as f:
    links = [link.strip() for link in f.readlines()]
    
label_list = ["news", "sports", "fashion", "finance", "ent", "tech", 
              "edu", "travel", "games", "auto"]


def get_information(i,url):
    try:
        result = {}
        res = requests.get(url)
        res.encoding = 'utf-8'
        result['label'] = 'unkonwn'
        for label in label_list:
            if label in url:
                result['label'] = label 
        
        soup = BeautifulSoup(res.text,'html.parser')
        result['url'] = url
        result['title']  = soup.select('.main-title')[0].text
        timesource = soup.select('span.date')[0].text
        result['dt']  = datetime.strptime(timesource,'%Y年%m月%d日 %H:%M')
        result['article']  = ''.join([p.text.strip() for p in soup.select('.article p')[:-1]])
        return tuple([i]+[v for k,v in result.items()])
    except Exception as e:
        print('error : {}'.format(e))
        return 


def save_info_to_db(inpu):
    no,link = inpu
    c = conn.cursor()
    info = get_information(no,link)

    if info:
        print('[+] success insert link into db, link id:{}'.format(no))
        
        c.execute("INSERT INTO news VALUES (?,?, ?, ?, ?, ?)", info)
        conn.commit()
    else:
        print("[-] link error: {}".format(link))


if __name__ == '__main__':
    conn = sqlite3.connect('./db/ir.db')
    # 多进程
    pool = multiprocessing.Pool()  
    # 多线程
    thread = threading.Thread(target=pool.map,args = (save_info_to_db,[link for link in enumerate(links)]))  
    thread.start()  
    thread.join()
