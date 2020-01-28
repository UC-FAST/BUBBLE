import sqlite3
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
    print(userID)
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
    print(userID)
    cursor.execute('SELECT id FROM userAuthorize WHERE id=?', (userID,))
    result = cursor.fetchall()
    cursor.close()
    db.commit()
    db.close()
    return result


def getFrendList(userID):
    db = sqlite3.connect('IMServerUser.db')
    cursor = db.cursor()
    cursor.execute('SELECT friends FROM userInfo WHERE id=?', (userID,))
    return _friendListDecode(cursor.fetchall()[0][0])
