#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jun  1 17:31:50 2019

@author: Adam

@E-mail: shengqiang.liu@videt.cn
"""
import sqlite3
import jieba
import os
# 配置参数
from config import *


class CreateIndex:

    def __init__(self):
        """
        bm25_hp_path: bm25的配置
        db_dir: 数据所在文件夹
        db： 数据库所在地址
        conn: 构建数据库链接
        """
        self.bm25_hp_path = bm25_hp_path
        self.db_dir = db_dir
        self.db = os.path.join(db_dir, db_file_name)
        self.conn = self.create_sqlite3_conn()

    def create_sqlite3_conn(self):
        """
        构建数据库连接
        :return:
        """
        if not os.path.exists(self.db_dir):
            os.makedirs(self.db_dir)
        return sqlite3.connect(self.db, check_same_thread=False)

    def get_information_from_db(self):
        """
        获取新闻id以及其标题信息
        """
        c = self.conn.cursor()
        sql = "select id,title from news"
        c.execute(sql)
        return c.fetchall()

    def clean_list(self, seg_list):
        """
        清洗分词后的文档
        :return: n:文档长度
                cleaned_dict:文档中的词频统计结果
        """
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

    def write_config(self, n, average):
        """
        配置参数写入本地保存
        :param n:  文档数目
        :param average:  平均文档长度
        """
        with open(self.bm25_hp_path, "w") as f:
            f.write("k = 1.5\n")
            f.write("b = 0.75\n")
            f.write("n = {}\n".format(n))
            f.write("average = {}\n".format(average))

    def write_postings_to_db(self):
        """
        位置信息写入数据库
        """

        c = self.conn.cursor()

        c.execute("""DROP TABLE IF EXISTS postings""")
        c.execute("""CREATE TABLE postings
                     (term TEXT PRIMARY KEY, df INTEGER, docs TEXT)""")

        for key, value in postings_lists.items():
            doc_list = '\n'.join(map(str, value[1]))
            t = (key, value[0], doc_list)
            c.execute("INSERT INTO postings VALUES (?, ?, ?)", t)

        self.conn.commit()

    def is_postings_tabel_exists(self):
        """
        判断新闻表是否存在
        :return: True or False
        """
        try:
            c = self.conn.cursor()
            c.execute("""SELECT count(1) from postings""")
            flag = c.fetchone()
            if flag[0]:
                return True
            else:
                return False
        except Exception as e:
            print("is postings tabel error :{}".format(e))
            return False

    def construct_postings_lists(self):
        """
        main, 计算索引列表,保存到数据库中
        :return:
        """
        # 文档信息
        documents = self.get_information_from_db()
        # 全部长度
        total_length = 0

        for id, document in documents:

            # 分词后的文章列表
            seg_list = jieba.lcut(document)
            # 计算分词后的长度，以及分词后词频统计结果
            length, cleaned_dict = self.clean_list(seg_list)
            # 计算总长度
            total_length = total_length + length

            # 循环词频统计结果
            for key, value in cleaned_dict.items():
                # 每个单词 其id为 所在文档， value为出现次数 length为文档长度
                d = [id, value, length]
                if key in postings_lists:
                    postings_lists[key][0] = postings_lists[key][0] + 1  # df++
                    postings_lists[key][1].append(d)
                else:
                    postings_lists[key] = [1, [d]]  # [df, [Doc]
            print("[+] id : {} create index done".format(id))
        # 计算平均长度
        average = total_length / len(documents)
        # 将配置参数写入config文件
        self.write_config(len(documents), average)
        # 将位置列表写入数据库
        self.write_postings_to_db()


CreateIndex = CreateIndex()


def create_index_start():
    flag = CreateIndex.is_postings_tabel_exists()
    if not flag:
        print('start create index...')
        CreateIndex.construct_postings_lists()
    else:
        print("index has already exist,dont create again.")
