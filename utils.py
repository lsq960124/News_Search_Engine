#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jun  1 17:31:50 2019

@author: Adam

@E-mail: shengqiang.liu@videt.cn
"""
import sqlite3
# 基础配置参数
from config import *
import os

# 数据库地址
db_path = os.path.join(db_dir,db_file_name)

class sqlit_utils:

    def __init__(self):
        # 创建数据库连接
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
    

    def fetchone_db(self, sql):
        """
        数据查询
        :param sql: sql语句
        :return:    sql结果
        """
        c = self.conn.cursor()
        c.execute(sql)
        return c.fetchone()

    def fetchall_db(self, sql):
        """
        数据查询
        :param sql: sql语句
        :return:    sql结果
        """
        c = self.conn.cursor()
        c.execute(sql)
        return c.fetchall()

    def exe(self, sql):
        """
        数据添加
        :param sql: sql语句
        """
        c = self.conn.cursor()
        c.execute(sql)
        self.conn.commit()
