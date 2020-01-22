import json


def register(userID, password, name, sex):
    with open('./IMServer/authorize.json') as f:
        r = json.load(f)
        r[userID] = password
    with open('./IMServer/authorize.json', 'w') as f:
        json.dump(r, f)
    with open('./IMServer/user.json') as f:
        r = json.load(f)
        r[userID] = {
            'name': name,
            'sex': sex,
            'friendList': {}
        }
    with open('./IMServer/user.json', 'w')as f:
        json.dump(r, f)


def addFriend(userID, *friend):
    vaild = True
    friend = list(friend)
    for _ in friend:
        if not hasUser(_):
            raise KeyError
    else:
        with open('./IMServer/user.json') as f:
            r = json.load(f)
            r[userID]['friendList'] = friend
        with open('./IMServer/user.json', 'w')as f:
            json.dump(r, f)


def hasUser(userID):
    with open('./IMServer/authorize.json') as f:
        r = json.load(f)
        return userID in r.keys()


def getFrendList(userID):
    with open('./IMServer/user.json') as f:
        return json.load(f)[userID]['friendList']
