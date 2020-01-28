# 消息处理模块

import sqlite3
import time
import logging
from IMServer.IMServerProtocol import *
from IMServer.serverAuthorize import *
import json


def _friendListEncode(friendList):
    friends = ''
    length = len(friendList) - 1
    for index, _ in enumerate(friendList):
        if index != length:
            friends += str(_) + ','
        else:
            friends += str(_)
    print(friends)
    return friends


def _friendListDecode(friends):
    print(friends)
    friends = friends.split(',')
    return [int(_) for _ in friends]


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


def register(userID, password):
    db = sqlite3.connect('IMServerUser.db')
    cursor = db.cursor()
    if hasUser(userID):
        return False
    cursor.execute('INSERT INTO userAuthorize (id, password) VALUES (?,?)', (userID, password))
    cursor.execute('INSERT INTO userInfo (id, name, sex, friends) VALUES (?,?,2,NULL)', (userID, userID))
    cursor.close()
    db.commit()
    db.close()
    return True


def addFriend(userID, *friend):
    db = sqlite3.connect('IMServerUser.db')
    cursor = db.cursor()
    cursor.execute('SELECT friends FROM userInfo WHERE id=?', (userID,))
    friendList = _friendListDecode(cursor.fetchall()[0][0])
    friend = set(friend)
    for _ in friend:
        if not hasUser(_):
            print(_)
            cursor.close()
            db.rollback()
            db.close()
            return False
        friendList.append(_)
    print(set(friendList))
    friendList = _friendListEncode(set(friendList))
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
    print(userID)
    db = sqlite3.connect('IMServerUser.db')
    cursor = db.cursor()
    cursor.execute('SELECT friends FROM userInfo WHERE id=?', (userID,))
    return _friendListDecode(cursor.fetchall()[0][0])


def handle(msg):
    if not msg:
        return None
    logging.info('Message {}'.format(msg))
    msg = json.loads(msg)
    text = dict()
    if isVaildData(msg):  # 数据合法性校验
        msg = msg['content']
        protocol = msg['protocol']
        if protocol == serverProtocol.login.value:  # 登录
            state = loginAuthorize(msg['msg']['userID'], msg['msg']['password'])
            text['msg'] = {'login': state}
            text['protocol'] = serverProtocol.relogin
            if state:
                print(msg['userID'], type(msg['userID']))
        elif protocol == serverProtocol.info.value:
            if msg['msg']['infoProtocol'] == infoProtocol.friendList.value:
                text['msg'] = {'friendList': getFriendList(msg['userID'])}
            elif msg['msg']['infoProtocol'] == infoProtocol.userRegister.value:
                text['msg'] = register(msg['msg']['userID'], msg['msg']['password'])
            text['protocol'] = serverProtocol.reinfo
        elif protocol:
            pass

        text['user'] = 0  # 服务器ID为0
        text['time'] = time.time()
    else:
        text['msg'] = {'infoProtocol': infoProtocol.invaildMessage}
        text['protocol'] = serverProtocol.reinfo
    text = packUp(text)
    logging.info('Return {}'.format(str(text)))
    return dumps(text)
