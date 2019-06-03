#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 31 19:57:55 2019

@author: Adam

@E-mail: shengqiang.liu@videt.cn
"""
import requests
import re
import sys
sys.setrecursionlimit(1000000000)

# 新闻
news = "https://news.sina.com.cn"
# 体育
sports = "http://sports.sina.com.cn/"

# 时尚
fashion = "https://fashion.sina.com.cn/"

# 财经
finance = "https://finance.sina.com.cn/"

# 娱乐
ent = "https://ent.sina.com.cn/"

# 科技
tech = "https://tech.sina.com.cn/"

# 教育
edu = "http://edu.sina.com.cn/"

# 旅游
travel = "http://travel.sina.com.cn/"

# 游戏
games = "http://games.sina.com.cn/"

# 汽车
auto = "http://auto.sina.com.cn/"

label_list = [news, sports, fashion, finance, ent, tech, 
              edu, travel, games, auto]

result = set()

def cawl_herfs(link,label,i):
    if len(result) > 1000*i:
        return 
    links = set()
    try:
        try:
            html = requests.get(link).content.decode("utf-8")
        except:
            html = requests.get(link).content.decode("gbk")
        pattern = 'href="(.*?)"'
        herfs = re.findall(pattern,html,re.S)
        for herf in herfs:
            if label in herf and "2019" in herf and herf.endswith("html") and herf not in links and herf not in result:
                print("[-] reslut lenght---> {}".format(len(result)))
                print("[+] herf--> {}".format(herf))
                links.add(herf)
                result.add(herf)
    except Exception as e:
        print("[-] error: {}".format(e))
        print("[-] error link: {}".format(link))
    for link in links:
        cawl_herfs(link,label,i)


if __name__ == "__main__":
    for i,label in enumerate(label_list):
        cawl_herfs(label,[name for name in globals() if globals()[name] is label][0],i+1) 
        
    with open("./data/links.txt","w+") as f:
        f.write("\n".join(result))