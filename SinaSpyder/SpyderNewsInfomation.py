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
import os
# 配置参数
from config import *


class SinaNewsInfomationSpyder:
    """爬取新闻内容"""

    def __init__(self):
        """
        links_dir： links数据所在的文件夹
        links_file_name： 保存links的文件夹名称
        db_path: 数据库所在地址

        """
        self.links_dir = links_dir
        self.links_file_name = links_file_name
        self.db_dir = db_dir
        self.db = os.path.join(db_dir, db_file_name)
        self.conn = self.create_sqlite3_conn()
        self.links = self.get_links()

    def create_sqlite3_conn(self):
        if not os.path.exists(self.db_dir):
            os.makedirs(self.db_dir)
        return sqlite3.connect(self.db, check_same_thread=False)

    def init_news_table(self):
        """
        初始化新闻的表
        :return:
        """
        c = self.conn.cursor()
        c.execute("""DROP TABLE IF EXISTS news""")
        c.execute("""CREATE TABLE news
                     (id INTEGER PRIMARY KEY, label TEXT, url TEXT, title TEXT , dt TEXT, article TEXT)""")
        self.conn.commit()

    def get_links(self):
        """
        获取链接列表
        :return: 链接列表
        """
        with open(os.path.join(self.links_dir, self.links_file_name), "r") as f:
            return [link.strip() for link in f.readlines()]

    def cawl_infomation(self, id, url):
        """
        爬取新闻内容
        :param id: 爬取url的标识
        :param url: url链接
        :return:
        """
        try:
            result = {}
            res = requests.get(url)
            res.encoding = 'utf-8'
            result['label'] = 'unkonwn'
            for label in label_list:
                if label in url:
                    result['label'] = label

            soup = BeautifulSoup(res.text, 'html.parser')
            result['url'] = url
            result['title'] = soup.select('.main-title')[0].text
            timesource = soup.select('span.date')[0].text
            result['dt'] = datetime.strptime(timesource, '%Y年%m月%d日 %H:%M')
            result['article'] = ''.join([p.text.strip() for p in soup.select('.article p')[:-1]])

            return tuple([id] + [v for k, v in result.items()])
        except Exception as e:
            print('cawl infomation error : {}'.format(e))
            return

    def is_news_tabel_exists(self):
        """
        判断新闻表是否存在
        :return: True or False
        """
        try:
            c = self.conn.cursor()
            c.execute("""SELECT count(1) from news""")
            flag = c.fetchone()
            if flag[0]:
                return True
            else:
                return False
        except:
            return False

    def save_info_to_db(self, id_url):

        c = self.conn.cursor()
        id, url = id_url
        info = self.cawl_infomation(id, url)
        if info:
            print('[+] success insert link into db, link id:{}'.format(id))
            c.execute("INSERT INTO news VALUES (?,?, ?, ?, ?, ?)", info)
            self.conn.commit()
        else:
            print("[-] cawl infomation has no text, lins: {}".format(url))


SinaNewsInfomationSpyder = SinaNewsInfomationSpyder()


def save_to_db(info):
    try:
        SinaNewsInfomationSpyder.save_info_to_db(info)
    except Exception as e:
        print("save to db error : {}".format(e))


def SinaNewsInfomationSpyder_start():
    """
    开启爬取新闻内容爬虫
    :return:
    """

    flag = SinaNewsInfomationSpyder.is_news_tabel_exists()

    if not flag:
        print('init news table...')
        SinaNewsInfomationSpyder.init_news_table()
        print('start to cawl information...')
        pool = multiprocessing.Pool()
        thread = threading.Thread(target=pool.map,
                                  args=(save_to_db, [link for link in enumerate(SinaNewsInfomationSpyder.links)]))

        thread.start()
        thread.join()
    else:
        print('information has alreadly cawl,dont cawl again...')
