# 消息处理模块

import sqlite3
import json


def loginAuthorize(userID, password):
    '''账号密码数据校验'''
    if not hasUser(userID):
        return False
    db = sqlite3.connect('IMServerUser.db')
    cursor = db.cursor()
    cursor.execute('SELECT password FROM userAuthorize WHERE id=?', (userID,))
    pwd = cursor.fetchall()
    cursor.close()
    db.commit()
    db.close()
    return pwd[0][0] == password


def getUserName(userID):
    db = sqlite3.connect('IMServerUser.db')
    cursor = db.cursor()
    cursor.execute('SELECT name FROM userInfo WHERE id=?', (userID,))
    name = cursor.fetchall()[0][0]
    cursor.close()
    db.commit()
    db.close()
    return name


def register(userID, password):
    db = sqlite3.connect('IMServerUser.db')
    cursor = db.cursor()
    if hasUser(userID):
        return False
    cursor.execute('INSERT INTO userAuthorize (id, password) VALUES (?,?)', (userID, password))
    friends = json.dumps({userID: str(userID)})
    cursor.execute('INSERT INTO userInfo (id, name, sex, friends) VALUES (?,?,2,?)', (userID, userID, friends))
    cursor.close()
    db.commit()
    db.close()
    return True


def changeName(userID, name):
    db = sqlite3.connect('IMServerUser.db')
    cursor = db.cursor()
    cursor.execute('UPDATE userInfo SET name=? WHERE id=?', (name, userID))
    cursor.close()
    db.commit()
    db.close()


def addFriend(userID, *friend):
    db = sqlite3.connect('IMServerUser.db')
    cursor = db.cursor()
    cursor.execute('SELECT friends FROM userInfo WHERE id=?', (userID,))
    friendList = json.loads(cursor.fetchall()[0][0])
    for _ in friend:
        if not hasUser(_):
            cursor.close()
            db.rollback()
            db.close()
            return False
        friendList[_] = getUserName(_)
    friendList = json.dumps(friendList)
    cursor.execute('UPDATE userInfo SET friends=? WHERE id=?', (friendList, userID))
    cursor.close()
    db.commit()
    db.close()
    return True


def hasUser(userID):
    db = sqlite3.connect('IMServerUser.db')
    cursor = db.cursor()
    cursor.execute('SELECT id FROM userAuthorize WHERE id=?', (userID,))
    result = cursor.fetchall()
    cursor.close()
    db.commit()
    db.close()
    return result


def getFriendList(userID):
    db = sqlite3.connect('IMServerUser.db')
    cursor = db.cursor()
    cursor.execute('SELECT friends FROM userInfo WHERE id=?', (userID,))
    result = json.loads(cursor.fetchall()[0][0])
    cursor.close()
    db.commit()
    db.close()
    return result
