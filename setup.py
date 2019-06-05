#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jun  1 18:17:05 2019

@author: Adam

@E-mail: shengqiang.liu@videt.cn
"""

if __name__ == '__main__':

    # 爬取链接
    from SinaSpyder.SpyderLinksFromSina import SinaNewsLinkSpyder
    SinaNewsLinkSpyder = SinaNewsLinkSpyder()
    SinaNewsLinkSpyder.start()
    # 爬取信息
    from SinaSpyder.SpyderNewsInfomation import SinaNewsInfomationSpyder_start
    SinaNewsInfomationSpyder_start()
    # 建立索引
    from SinaSpyder.CreateBM25Index import create_index_start
    create_index_start()
    # 计算推荐表
    from SinaSpyder.CountRecommendNews import count_recommend_start
    count_recommend_start()