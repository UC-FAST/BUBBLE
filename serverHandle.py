import threading
import IMServer

a = IMServer.IMServerSocket('127.0.0.1', 8760)
mainloop=threading.Thread(target=a.mainLoop)
cleanUp=threading.Thread(target=a.userListCleanup)
mainloop.start()
cleanUp.start()