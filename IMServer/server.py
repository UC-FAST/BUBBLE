import sqlite3
import json


def friendListEncode(friendList):
    friends = ''
    length = len(friendList) - 1
    for index, _ in enumerate(friendList):
        if index != length:
            friends += str(_) + ','
        else:
            friends += str(_)
    return friends


def friendListDecode(friends):
    friends = friends.split(',')
    return [int(_) for _ in friends]


def loginAuthorize(msg):
    '''账号密码数据校验'''
    if not hasUser(msg['userID']):
        return False
    db = sqlite3.connect('IMServerUser.db')
    cursor = db.cursor()
    cursor.execute('SELECT password FROM userAuthorize WHERE id=?', msg['userID'])
    pwd = cursor.fetchall()
    cursor.close()
    db.commit()
    db.close()
    return pwd[0][0] == msg['password']


def register(userID, password):
    db = sqlite3.connect('IMServerUser.db')
    cursor = db.cursor()
    if hasUser(userID):
        return False
    cursor.execute('INSERT INTO userAuthorize (id, password) VALUES (?,"?"),', (userID, password))
    cursor.execute('INSERT INTO userInfo (id, name, sex, friends) VALUES (?,"?",2,NULL)', (userID, userID))
    cursor.close()
    db.commit()
    db.close()
    return True


def addFriend(userID, *friend):
    db = sqlite3.connect('IMServerUser.db')
    cursor = db.cursor()
    cursor.execute('SELECT friends FROM userInfo WHERE id=?', userID)
    friendList = list(cursor.fetchall()[0])

    friend = set(friend)
    for _ in friend:
        if not hasUser(_):
            cursor.close()
            db.rollback()
            db.close()
            return False
        friendList.append(_)
    friendList = friendListEncode(set(friendList))
    cursor.execute('UPDATE userInfo SET friends=? WHERE id=?', (friendList, userID))
    cursor.close()
    db.commit()
    db.close()


def hasUser(userID):
    db = sqlite3.connect('IMServerUser.db')
    cursor = db.cursor()
    cursor.execute('SELECT id FROM userAuthorize WHERE id=?', (userID,))
    result = cursor.fetchall()
    cursor.close()
    db.commit()
    db.close()
    return result


def getFrendList(userID):
    db = sqlite3.connect('IMServerUser.db')
    cursor = db.cursor()
    cursor.execute('SELECT friends FROM userInfo WHERE id=?', userID)
    return friendListDecode(cursor.fetchall()[0])
