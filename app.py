#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jun  1 17:31:50 2019

@author: Adam

@E-mail: shengqiang.liu@videt.cn
"""
import sqlite3
from flask import Flask, request, render_template, url_for,redirect,session
from search import search_use_bm25_model
from search import conn
from search import init_history_db
from search import update_history
from config import label_list
from utils import sqlit_utils
sqlit_utils = sqlit_utils()
app = Flask(__name__)
app.config['SECRET_KEY'] = '470581985@qq.com'

@app.route("/")
def root():
    '''
    主页面
    ''' 
    login, userid, error = False, '', False
    if 'userid' in session:
        login, userid = True, session['userid']
    news = []
    try:
        c = conn.cursor()
        c.execute('select id,title from news limit 10')
        news = c.fetchall()
    except Exception as e:
        print("hots news error:", e)

    history = []
    try:
        c.execute('''select a.id,a.title
                            from news as a  inner join
                            (select id from history ORDER BY times limit 10) as b
                            on  a.id=b.id''')
        history = c.fetchall()
    except Exception as e:
        print("history news error:", e)

    return render_template("Index.html", 
                            hots=news, 
                            history=history,
                            login=login,
                            useid=userid)

@app.route("/search", methods=['POST', 'GET'])
def search():
    """
    新闻检索
    :return: Search.html
    """
    login, userid, error = False, '', False
    if 'userid' in session:
        login, userid = True, session['userid']
    docs = []
    result = {label: [] for label in label_list}
    keyword = ''
    try:
        if request.method == 'GET':
            keyword = request.values.get('keyword')
            keyword = keyword.strip()
            if keyword:
                docs = search_use_bm25_model(keyword)
                for doc in docs:
                    for label in label_list:
                        if doc[1] == label:
                            result[label].append(doc)
    except Exception as e:
        print('search engine error:',e)
    if docs:
        return render_template("Search.html",
                                 docs = docs,
                                 result = result,
                                 key = keyword,
                                 login=login,
                                 useid=userid
                                 )     
    else:
        return redirect(url_for('root'))


@app.route("/news", methods=['POST', 'GET'])
def newsinfo():
    """
    文章详情
    :return: news.html
    """
    login, userid, error = False, '', False
    if 'userid' in session:
        login, userid = True, session['userid']
    init_history_db()

    news = []
    recommend_news = []
    try:
        if request.method == 'GET':
            newsid = request.args.get('newsid')

            update_history(newsid)

            c = conn.cursor()
            c.execute('select * from news where id= {} '.format(newsid))
            news = c.fetchone()

            c.execute('select * from recommend where id={}'.format(newsid))
            recommends = c.fetchone()

            recommends = recommends[1:]
            recommend_news = []
            for recommend_id in recommends :
                c.execute('select id,title from news where id={}'.format(recommend_id))
                recommend_news.append(c.fetchone())


    except Exception as e:
        print('news info error:',e)

    return render_template('News.html',
                            doc=news, 
                            recommends=recommend_news,
                            login=login,
                            useid=userid)

def is_valid(username, password):
    """
    登录验证
    :param username: 用户名
    :param password: 密码
    :return: True/False
    """
    try:
        sql = "SELECT username, password FROM user where username='{}' and password ='{}'".format(username,
                                                                                            password)
        result =  sqlit_utils.fetchone_db(sql)

        if result:
            print('username:{},password:{}: has login success'.format(username, password))
            return True
        else:
            print('username:{},password:{}: has login filed'.format(username, password))
            return False
    except Exception as e:
        print('username:{},password:{}: has login error'.format(username, password))
        return False

@app.route("/login", methods=['POST', 'GET'])
def login():
    """
    登录页提交
    :return: Login.html
    """
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'admin' and username == password:
            session['userid'] = username
            return render_template('Admin.html',userid= 'admin')
        if is_valid(username, password):
            session['userid'] = username
            return redirect(url_for('root'))
        else:
            error = '账号密码输入错误'
            return render_template('Login.html', error=error)

@app.route("/logout")
def logout():
    """
    退出登录，注销
    :return: root
    """
    session.pop('userid', None)
    return redirect(url_for('root'))

@app.route("/loginForm")
def loginForm():
    """
    跳转登录页
    :return: Login.html
    """
    if 'userid' in session:
        return redirect(url_for('root'))
    else:
        return render_template('Login.html', error='')


@app.route("/registerationForm")
def registrationForm():
    """
    跳转注册页
    :return: Register.html
    """
    return render_template("Register.html")


@app.route("/adminuser", methods=["GET", "POST"])
def adminuser():
    '''
    管理用户页面
    '''
    users = []
    try:
        userid = session['userid']
        sql = "select * from user limit 20 "
        users = sqlit_utils.fetchall_db(sql)
        print('adminuser',users)
        users = [ [q,k,v] for q,k,v in users]
        print('adminuser',users)
        return render_template('AdminUser.html',users = users, error=False, userid=userid)
    except Exception as e:
        print("Admin User info error: {}".format(e))
        users = []
        return redirect('AdminUser.html',users = users, error=False, userid="admin")

@app.route("/keyword", methods=["GET", "POST"])
def keyword():
    '''
    关键字查询用户
    '''
    users = []
    try:
        userid = session['userid']
        if request.method == 'POST':
            keyword = request.form['keyword']
            if keyword:
                sql = "select * from user where username like '%{}%' limit 20 ".format(keyword)
                users = sqlit_utils.fetchall_db(sql)
                sers = [ [q,k,v] for q,k,v in users]
            return render_template('AdminUser.html',users = users, userid=userid)
    except Exception as e:
        print("keyword info  error: {}".format(e))
        return render_template('AdminUser.html',users = users, userid="admin")

@app.route("/register", methods=["GET", "POST"])
def register():
    """
    注册
    :return: Register.html
    """
    try:
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            age = request.form['age']

            try:
                sql = "insert into user (username,password,age) values ('{}','{}','{}')".format(username, password, age)
                sqlit_utils.exe(sql)
                print("username:{},password:{},age:{} register success".format(username, password, age))
            except Exception as e:
                print("username:{},password:{},age:{} register filed".format(username, password, age))
            return render_template('Login.html')
    except Exception as e:
        print("register function error: {}".format(e))
        return render_template('Register.html', error='注册出错')

@app.route("/delete_user", methods=['POST', 'GET'])
def delete_user():
    '''
    删除用户
    '''
    userid = session['userid']
    try:
        if request.method == 'GET':
            userid = request.values.get('userid')
            sql = '''DELETE  FROM user WHERE username="{0}" '''.format(userid)
            sqlit_utils.exe(sql)
            print("delete user  success,sql:{}".format(sql))
    except Exception as e:
        print("delete User books error: {}".format(e))
    return redirect(url_for('adminuser'))




if __name__ == '__main__':
    app.run(debug=True, port=8080)