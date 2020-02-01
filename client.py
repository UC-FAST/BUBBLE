import IMClient as im
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
                im.mainFunc(a)

            elif choice == '2':
                im.register(a)

            elif choice == '3':
                exit(0)

        except loginError:
            print('登录失败，请检查账号和密码')
