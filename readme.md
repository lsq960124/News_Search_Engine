# 新闻搜索引擎

## 代码介绍

```
----新闻搜索引擎\
    |----word2vec\                      推荐算法使用到的是doc2vec，这个doc2vec的模型
    |    |----model_doc2vec.trainables.syn1neg.npy
    |    |----model_doc2vec
    |    |----model_doc2vec.wv.vectors.npy
    |----spyder_news_infomation.py      从已经爬取到的网页链接中爬取详细内容，存入数据库中。
    |----get_links_from_sina.py         从新浪新闻主页中爬取网页链接，使用算法逻辑是 广度优先遍历
    |----config.py                      配置参数
    |----create_index.py                构建索引
    |----links.txt                      网页链接
    |----readme.md
    |----static\                        前端的静态文件
    |----templates\                     html的模板
    |    |----Index.html
    |    |----News.html
    |    |----Search.html
    |----app.py                          服务器入口文件，在这个文件夹启动服务器
    |----count_recommend_news.py         计算推荐表信息
    |----search.py                       搜索引擎的搜索程序
    |----ir.db                           数据库文件

```

### 项目启动方式


启动 `app.py` 即可启动项目


* 如果需要重新爬取新的链接，重新构建索引，重新计算推荐情况。
* step1： 运行 `get_links_from_sina.py` 获取链接；运行它会生成一个 links.txt
* step2： 运行`spyder_news_infomation.py` 爬取链接的内容，存到数据库中
* step3： 运行`create_index.py` 为搜索引擎构建索引
* step4： 运行`count_recommend_news.py` 计算针对每个新闻的推荐新闻
* step5： 运行 `app.py` 即可启动项目

