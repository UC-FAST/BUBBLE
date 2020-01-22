import json


def register(userID, password):
    with open('./IMServer/authorize.json') as f:
        r = json.load(f)
        if hasUser(userID):
            raise KeyError
        r[userID] = password
    with open('./IMServer/authorize.json', 'w') as f:
        json.dump(r, f)
    with open('./IMServer/user.json') as f:
        r = json.load(f)
        r[userID] = {
            'name': None,
            'sex': None,
            'friendList': {}
        }
    with open('./IMServer/user.json', 'w')as f:
        json.dump(r, f)


def addFriend(userID, *friend):
    vaild = True
    friend = list(set(friend))
    for _ in friend:
        if not hasUser(_):
            raise KeyError
    else:
        with open('./IMServer/user.json') as f:
            r = json.load(f)
            friends = set(r[userID]['friendList'])
            for _ in friend:
                friends.add(_)
            r[userID]['friendList'] = list(friends)
        with open('./IMServer/user.json', 'w')as f:
            json.dump(r, f)


def hasUser(userID):
    with open('./IMServer/authorize.json') as f:
        r = json.load(f)
        return userID in r.keys()


def getFrendList(userID):
    with open('./IMServer/user.json') as f:
        return json.load(f)[userID]['friendList']
