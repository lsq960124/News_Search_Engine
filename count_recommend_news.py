#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jun  1 17:31:50 2019

@author: Adam

@E-mail: shengqiang.liu@videt.cn
"""

import sqlite3
import gensim
import numpy as np
import os
import jieba
import threading
import multiprocessing
from gensim.models.doc2vec import Doc2Vec, LabeledSentence
TaggededDocument = gensim.models.doc2vec.TaggedDocument

db_path = './db/ir.db'
conn = sqlite3.connect(db_path)

def create_recommend_db():
    c = conn.cursor()
        
    c.execute('''DROP TABLE IF EXISTS recommend''')
    c.execute('''CREATE TABLE recommend
                 (id INTEGER PRIMARY KEY, first INTEGER, second INTEGER,
                 third INTEGER, fourth INTEGER, fifth INTEGER)''')

    conn.commit()



def write_recommend_to_db(recommends):
 
    c = conn.cursor()

    c.execute("INSERT INTO recommend VALUES (?, ?, ?, ?, ?, ?)", tuple(recommends))

    conn.commit()



def select_documents_from_db(db_path):

    c = conn.cursor()
    c.execute('''select id,article from news''')
    return c.fetchall()


def get_corpus():

    documents = select_documents_from_db(db_path)
    train_docs = []
    for id, text in documents:
        word_list = [word for word in jieba.cut(text)]
        length = len(word_list)
        document = TaggededDocument(word_list, tags=[id])
        train_docs.append(document)
    return train_docs

def train(x_train, size=200, epoch_num=1):

    model_dm = Doc2Vec(x_train, min_count=1, window=3, vector_size=size, sample=1e-3, negative=5, workers=4)
    model_dm.train(x_train, total_examples=model_dm.corpus_count, epochs=70)
    model_dm.save('word2vec/model_doc2vec')
    return model_dm

def predict(docs):
    try:
        id,sentence = docs
        text_raw = [word for word in jieba.cut(sentence)]
        inferred_vector_dm = model_dm.infer_vector(text_raw)
        sims = model_dm.docvecs.most_similar([inferred_vector_dm], topn=6)
        if sims:
            sims = [id] + [int(i[0]) for i in sims if int(i[0]) != id]
            print(sims)
            print("[+] id: {}".format(id))
            print("[+] recommend id : {}".format(sims))
            write_recommend_to_db(sims)
    except:
        print("[-] id error: {}".format(id))


if __name__ == '__main__':
    if not os.path.exists("word2vec/model_doc2vec"):
        x_train = get_corpus()
        model_dm = train(x_train)
    else:
        model_dm = Doc2Vec.load("word2vec/model_doc2vec")

    create_recommend_db()

    documents = select_documents_from_db(db_path)
    
    pool = multiprocessing.Pool()  
    # 多进程  
    thread = threading.Thread(target=pool.map,args = (predict,[docs for docs in documents]))  
    thread.start()  
    thread.join()


