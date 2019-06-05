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

label_list = {"news":news, "sports":sports, "fashion":fashion, "finance":finance, "ent":ent, "tech":tech, 
              "edu":edu, "travel":travel, "games":games, "auto":auto}

# 每个新闻爬取最多多少条新闻。做一个限制，不然会递归爬完新浪新闻。会很耗时
number_flag = 2000

# 数据库文件夹
db_dir = './db/'
db_file_name = 'ir.db'

# 爬取链接保存的文件夹
links_dir = "./data/"
links_file_name = "links.txt"

# word2vec model
word2vec_dir = './word2vec/'
word2vec_file_name = 'model_doc2vec'

# bm25 model hp dir
bm25_hp_path = './SinaSpyder/bm25_config.py'

# 位置片段
postings_lists = {}