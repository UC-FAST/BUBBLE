import IMClient as im
from os.path import exists
from IMClient.user import loginError

if __name__ == '__main__':
    while True:
        try:
            if not exists('bubble.json'):
                im.createConfigFile()
            im.welcome()
            a = im.userHandle(im.readConfigFile()['server_address'], int(im.readConfigFile()['server_port']))
            #a=im.userHandle('127.0.0.1',18760)
            print(a.getServerTips())
            while True:
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
