import IMClient as im
from time import sleep
from IMClient.user import loginError

if __name__ == '__main__':
    while True:
        try:
            im.welcome()
            a = im.userHandle()
            print(a.getServerTips())
            im.showStartUpMenu()
            choice = input('>')
            if choice == '1':
                id = input('User ID: ')
                pwd = input('Password: ')
                print(a.login(872702913, '(imp@h01)'))
                print(a.getFriendList())
                a.sendMsg(872702913,'wew')
                a.getNewMsg()
            if choice == '2':
                print('23')
                userID = input('User ID: ')
                pwd = input('Password: ')
                msg = a.userRegister(userID, pwd)
                print(msg)

            if choice == '3':
                exit(0)

        except loginError:
            print('登录失败，请检查账号和密码')
