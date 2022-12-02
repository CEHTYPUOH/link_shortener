from flask import Flask, request, redirect, jsonify, make_response
from flask_jwt_extended import create_access_token, JWTManager, get_jwt_identity, jwt_required
import sqlite3
import uuid
import hashlib
import random
from werkzeug.security import generate_password_hash, check_password_hash

con = sqlite3.connect('database.db')
cur = con.cursor()

cur.execute("""CREATE TABLE IF NOT EXISTS users(id INTEGER, username TEXT UNIQUE, password TEXT, PRIMARY KEY (id AUTOINCREMENT))""")
con.commit()
cur.execute("""CREATE TABLE IF NOT EXISTS refs (id INTEGER, ref TEXT, ref_kind TEXT, ref_owner TEXT, num_clicks INTEGER, PRIMARY KEY (id AUTOINCREMENT))""")
con.commit()


con.close()

is_auth = False
user_id = 0


def reg(data):
    global is_auth
    global user_id
    con = sqlite3.connect('database.db')
    cur = con.cursor()
    if cur.execute("""SELECT username FROM users WHERE username=?""", (data[0],)).fetchone() == None:
        cur.execute(
            """INSERT INTO users(username, password) VALUES(?, ?)""", (data[0], data[1]))
        con.commit()
        is_auth = True
        user_id = cur.execute(
            """SELECT id FROM users WHERE username=?""", (data[0],)).fetchone()
    con.close()
    return is_auth


def auth(data):
    global is_auth
    global user_id
    con = sqlite3.connect('database.db')
    cur = con.cursor()
    if cur.execute("""SELECT id FROM users WHERE username=? AND password=?""", (data[0], data[1])).fetchone() != None:
        is_auth = True
        user_id = cur.execute(
            """SELECT id FROM users WHERE username=?""", (data[0],)).fetchone()
    con.close()
    return is_auth


def create_short_link(data):
    con = sqlite3.connect('database.db')
    cur = con.cursor()
    flag = False
    short_ref = hashlib.md5(data[0].encode()).hexdigest()[
        :random.randint(8, 12)]
    cur.execute("""INSERT INTO refs(full_ref, short_ref, ref_kind, ref_owner, num_clicks) VALUES(?,?,?,?,?)""",
                (data[0], short_ref, data[1], data[2][0], 0))
    con.commit()
    if cur.execute("""SELECT id FROM refs WHERE full_ref=?""", (data[0],)).fetchone() != None:
        flag = True
    con.close()
    return flag


# user_address = hashlib.md5(address.encode()).hexdigest()[:random.randint(8, 12)]


app = Flask(__name__)


@app.route('/',)
def nothing():
    return "Hello!"


@app.route('/register', methods=['GET', 'POST'])
def render_reg():
    text = ''
    if request.method == 'POST':
        username = str(request.json.get('username'))
        password = str(request.json.get('password'))
        flag = reg([username, password])
        if flag == True:
            text = 'Bы успешно зарегистрировались'
        else:
            text = 'Пользователь с таким логином уже существует'
    return make_response(text)


@app.route('/authorize', methods=['GET', 'POST'])
def render_auth():
    text = ''
    if request.method == 'POST':
        username = str(request.json.get('username'))
        password = str(request.json.get('password'))
        flag = auth([username, password])
        if flag == True:
            text = 'Bы успешно авторизовались'
        else:
            text = 'Неправильный логин или пароль'
    return make_response(text)


@app.route('/create_link', methods=['GET', 'POST'])
def render_create_link():
    text = ''
    if request.method == 'POST':
        if is_auth == True:
            link = str(request.json.get('link'))
            kind = str(request.json.get('kind'))
            flag = create_short_link([link, kind, user_id])
            if flag == True:
                text = 'Ссылка успешно сокращена'
            else:
                text = 'Операция по сокращению ссылки провалена'
            return make_response(text)


@app.route('/links', methods=['GET', 'POST'])
def render_links():
    pass


if __name__ == '__main__':
    app.run(debug=True)
