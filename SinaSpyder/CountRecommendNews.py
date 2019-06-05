#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jun  1 17:31:50 2019

@author: Adam

@E-mail: shengqiang.liu@videt.cn
"""

import sqlite3
import gensim
import jieba
import threading
import multiprocessing
import os
from gensim.models.doc2vec import Doc2Vec

TaggededDocument = gensim.models.doc2vec.TaggedDocument
# 配置参数
from config import *


class CountRecommend:

    def __init__(self):

        self.db_dir = db_dir
        self.db = os.path.join(db_dir, db_file_name)
        self.conn = self.create_sqlite3_conn()
        if not self.is_recommend_tabel_exists():
            self.init_recommend_db()
        self.word2vec_dir = word2vec_dir
        self.word2vec_path = os.path.join(word2vec_dir, word2vec_file_name)
        self.model = self.train_or_load_model()

    def create_sqlite3_conn(self):
        if not os.path.exists(self.db_dir):
            os.makedirs(self.db_dir)
        return sqlite3.connect(self.db, check_same_thread=False,timeout=10)

    def init_recommend_db(self):
        c = self.conn.cursor()

        c.execute('''DROP TABLE IF EXISTS recommend''')
        c.execute('''CREATE TABLE recommend
                     (id INTEGER PRIMARY KEY, first INTEGER, second INTEGER,
                     third INTEGER, fourth INTEGER, fifth INTEGER)''')
        print("init recommend db ....")
        self.conn.commit()

    def write_recommend_to_db(self, recommends):
        c = self.conn.cursor()
        sql = "INSERT INTO recommend VALUES (?, ?, ?, ?, ?, ?)", tuple(recommends)
        print(sql)
        c.execute(sql)
        self.conn.commit()

    def select_documents_from_db(self):
        c = self.conn.cursor()
        c.execute('''select id,article from news''')
        return c.fetchall()

    def get_corpus(self):
        documents = self.select_documents_from_db()
        train_docs = []
        for id, text in documents:
            word_list = [word for word in jieba.cut(text)]
            document = TaggededDocument(word_list, tags=[id])
            train_docs.append(document)
        return train_docs

    def train(self, size=200):
        x_train = self.get_corpus()
        model = Doc2Vec(x_train, min_count=1, window=3, vector_size=size, sample=1e-3, negative=10, workers=6)
        model.train(x_train, total_examples=model.corpus_count, epochs=100)
        model.save(self.word2vec_path)
        return model

    def train_or_load_model(self):
        if not os.path.exists(self.word2vec_dir):
            os.makedirs(self.word2vec_dir)
        if not os.path.exists(self.word2vec_path):
            model = self.train()
        else:
            model = Doc2Vec.load(self.word2vec_path)
        return model

    def is_recommend_tabel_exists(self):
        '''
        判断推荐表是否存在
        :return: True or False
        '''
        try:

            c = self.conn.cursor()
            c.execute('''SELECT count(1) from recommend''')
            flag = c.fetchone()

            if flag[0]:
                return True
            else:
                return False
        except Exception as e:
            print("is recommend tabel error :{}".format(e))
            return False


CountRecommend = CountRecommend()

documents = CountRecommend.select_documents_from_db()
length = len(documents)
new_recommends = []
def predict(docs):
    try:
        id, sentence = docs
        text_raw = [word for word in jieba.cut(sentence)]
        inferred_vector_dm = CountRecommend.model.infer_vector(text_raw)
        sims = CountRecommend.model.docvecs.most_similar([inferred_vector_dm], topn=6)
        if sims:
            sims = [id] + [int(i[0]) for i in sims if int(i[0]) != id]
            sims = sims[:6]
            print("[+] id :{} recommend done, \t {}%".format(id, id*100//length))
            new_recommends.append(sims)
            
    except  Exception as e:
        print("[-] id : {},error:{}".format(id, e))

def count_recommend_start():
    flag = CountRecommend.is_recommend_tabel_exists()
    if not flag:
        print("start count recommend ...")
        pool = multiprocessing.Pool()
        # 多进程
        thread = threading.Thread(target=pool.map, args=(predict, [docs for docs in documents]))
        thread.start()
        thread.join()
        for new_recommend in new_recommends:
            CountRecommend.write_recommend_to_db(new_recommend)
    else:
        print("count recommend has already exists,dont create again...")
