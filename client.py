import IMClient as im
from IMClient.user import loginError

if __name__ == '__main__':
    while True:
        try:
            im.welcome()
            im.showStartUpMenu()
            choice = input('>')
            a = im.userHandle()
            if choice == '1':
                id = input('User ID: ')
                pwd = input('Password: ')
                a.login(872702913, '(imp@h01)')
                print(a.getFriendList())
                im.showMainMenu()
                choice = input('>')
            if choice == '2':
                print('23')
                userID = input('User ID: ')
                pwd = input('Password: ')
                msg=a.userRegister(userID, pwd)
                print(msg)


            if choice == '3':
                exit(0)

        except loginError:
            print('登录失败，请检查账号和密码')
