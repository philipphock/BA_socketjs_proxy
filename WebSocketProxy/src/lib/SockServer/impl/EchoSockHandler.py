'''
Created on Aug 8, 2011

@author: phil
'''
from SockServer.utils.basic.BasicSocketHandler import BasicSocketHandler

class EchoSockHandler(BasicSocketHandler):
    ''' a basic EchoServer for test purpose and illustration'''

    def __init__(self):
        BasicSocketHandler.__init__(self)

        
    def recv(self,msg):
        if(msg==b"q"):
            print("command: quit")
            self._cfg["server"].doClose()
        if(msg==b"d"):
            print("command: quit")
            self.doDisconnect()
        else:
            if msg==b"l" :
                tm=self._cfg["server"].taskManager
                i=str(tm.getSize())+" "+str(tm.getCapacity())
                print(i)
            else:
                self.client.send(b" >"+msg)
        