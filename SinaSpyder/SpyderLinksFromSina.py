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
import os
# 配置参数
from config import *

# 递归次数限制
sys.setrecursionlimit(1000000000)


class SinaNewsLinkSpyder:
    """爬取新浪新闻的指定频道链接"""

    def __init__(self):
        """
        links：抓取的网页url列表
        number_flag：每个频道抓取的url条数限制
        links_dir： links数据所在的文件夹
        links_file_name： 保存links的文件夹名称
        """
        self.links = set()
        self.number_flag = number_flag
        self.links_dir = links_dir
        self.links_file_name = links_file_name

    def cawl_links(self, root_link, channel, channel_number):
        """
        针对每个频道爬取对应的链接
        :param root_link: 入口链接
        :param channel: 所在频道 “news”，“sports”....so on
        :param channel_number: 频道对应的编号
        :return:
        """
        # 如果保持的links的长度大于number_flag限制的长度,那么就跳出递归
        if len(self.links) > self.number_flag * channel_number:
            return

        root_links = set()
        try:
            try:
                html = requests.get(root_link).content.decode("utf-8")
            except Exception as e:
                print('"utf-8" cant cawl link: {}, error : {}'.format(root_link, e))
                html = requests.get(root_link).content.decode("gbk")
            pattern = 'href="(.*?)"'
            herfs = re.findall(pattern, html, re.S)
            for herf in herfs:
                if channel in herf and "2019" in herf and herf.endswith(
                        "html") and herf not in root_links and herf not in self.links:
                    print("[-] reslut lenght---> {}".format(len(self.links)))
                    print("[+] herf--> {}".format(herf))
                    root_links.add(herf)
                    self.links.add(herf)
        except Exception as e:
            print("[-] error: {}".format(e))
            print("[-] error link: {}".format(root_links))

        # 递归爬取当前频道下的所有新闻
        for link in root_links:
            self.cawl_links(link, channel, channel_number)

    def start(self):
        """
        开启爬虫
        :return:
        """
        links_path = os.path.join(self.links_dir, self.links_file_name)
        # 如果没有爬取过链接，再爬取一次
        if not os.path.exists(links_path):
            print("start cawl sina news...")
            # 如果没有保存的文件 创建一个
            if not os.path.exists(links_dir):
                os.makedirs(links_dir)
            # 训练新浪新闻的链接列表，深度优先遍历新闻列表
            for channel_number, channel in enumerate(label_list):
                self.cawl_links(label_list[channel], channel, channel_number + 1)

            # 存入本地文件夹中
            with open(links_path, "w+") as f:
                f.write("\n".join(self.links))
        else:
            print('links has already cawl done，dont need cawl again')
