# 消息处理模块

import sqlite3
import json
from collections import defaultdict


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


def getUserInfo(userID):
    db = sqlite3.connect('IMServerUser.db')
    cursor = db.cursor()
    try:
        cursor.execute('SELECT id, name, sex FROM userInfo WHERE id=?', (userID,))
        return cursor.fetchall()[0]
    except sqlite3.OperationalError:
        return False
    finally:
        cursor.close()
        db.commit()
        db.close()


def register(userID, password):
    db = sqlite3.connect('IMServerUser.db')
    cursor = db.cursor()
    if hasUser(userID):
        return False
    cursor.execute('INSERT INTO userAuthorize (id, password) VALUES (?,?)', (userID, password))
    friends = json.dumps([userID])
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
    return True


def changeSex(userID, sex):
    db = sqlite3.connect('IMServerUser.db')
    cursor = db.cursor()
    cursor.execute('UPDATE userInfo SET sex=? WHERE id=?', (sex, userID))
    cursor.close()
    db.commit()
    db.close()
    return True


def changePassword(userID, oldPassword, newPassword):
    db = sqlite3.connect('IMServerUser.db')
    cursor = db.cursor()
    cursor.execute('SELECT password FROM userAuthorize WHERE id=?', (userID,))
    if oldPassword == cursor.fetchall()[0][0]:
        cursor.execute('UPDATE userAuthorize SET password=? WHERE id=?', (newPassword, userID))
        cursor.close()
        db.commit()
        db.close()
        return True
    else:
        return False


def addFriend(userID, *friends):
    db = sqlite3.connect('IMServerUser.db')
    cursor = db.cursor()
    cursor.execute('SELECT friends FROM userInfo WHERE id=?', (userID,))
    friendList = json.loads(cursor.fetchall()[0][0])
    for _ in friends:
        if not hasUser(_):
            cursor.close()
            db.rollback()
            db.close()
            return False
        friendList.append( getUserInfo(_)[0])
        friendList=list(set(friendList))
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
    result = cursor.fetchall()[0][0]
    cursor.close()
    db.commit()
    db.close()
    return json.loads(result)


def getNewMsg(userID):
    db = sqlite3.connect('IMServerUser.db')
    cursor = db.cursor()
    cursor.execute('SELECT fromUser, time, msg,type FROM userMsg WHERE toUser=?', (userID,))
    result = defaultdict(list)
    for fromUser, timeStamp, msg, msgType in cursor.fetchall():
        result[timeStamp].append({'fromUser': fromUser, 'msg': msg, 'type': msgType})
    cursor.close()
    db.commit()
    db.close()
    return result


def storageMsg(fromUser, toUser, time, msg, type=0):
    db = sqlite3.connect('IMServerUser.db')
    cursor = db.cursor()
    cursor.execute('INSERT INTO userMsg(toUser, fromUser, time, msg,type) VALUES (?,?,?,?,?)',
                   (toUser, fromUser, time, msg, type))
    cursor.close()
    db.commit()
    db.close()


def delMessage(toUser):
    db = sqlite3.connect('IMServerUser.db')
    cursor = db.cursor()
    cursor.execute('DELETE FROM userMsg WHERE toUser=?', (toUser,))
    cursor.close()
    db.commit()
    db.close()
    return True
