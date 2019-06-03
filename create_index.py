#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jun  1 17:31:50 2019

@author: Adam

@E-mail: shengqiang.liu@videt.cn
"""
import sqlite3
import jieba

# 位置片段
postings_lists = {}
# 数据库地址
db_path = './db/ir.db'

'''查询信息'''
def get_information_from_db(dbpath):
    conn = sqlite3.connect(dbpath)
    c = conn.cursor()
    sql = "select id,title from news"
    c.execute(sql)
    return c.fetchall()

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

'''配置参数'''
def write_config(n,average):
    with open("config.py","w") as f:
        f.write("db_path = 'ir.db'\n")
        f.write("k = 1.5\n")
        f.write("b = 0.75\n")
        f.write("n = {}\n".format(n))
        f.write("average = {}\n".format(average))


'''写入数据库'''
def write_postings_to_db(db_path):
        
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
     
    c.execute('''DROP TABLE IF EXISTS postings''')
    c.execute('''CREATE TABLE postings
                 (term TEXT PRIMARY KEY, df INTEGER, docs TEXT)''')
     
    for key, value in postings_lists.items():
        doc_list = '\n'.join(map(str, value[1]))
        t = (key, value[0], doc_list)
        c.execute("INSERT INTO postings VALUES (?, ?, ?)", t)

    conn.commit()
    conn.close()
    
'''main'''
def construct_postings_lists(db_path):
    
    # 文档信息
    documents = get_information_from_db(db_path)
    # 全部长度
    total_length = 0
    
    for id, document in documents:
        
        # 分词后的文章列表
        seg_list = jieba.lcut(document)
        # 计算分词后的长度，以及分词后词频统计结果
        length, cleaned_dict = clean_list(seg_list)
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
        print("[+] id : {} ".format(id))
    # 计算平均长度
    average = total_length / len(documents)
    # 将配置参数写入config文件
    write_config(len(documents),average)
    # 将位置列表写入数据库
    write_postings_to_db(db_path)

if __name__ == "__main__":
    construct_postings_lists(db_path)
