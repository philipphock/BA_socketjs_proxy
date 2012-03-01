'''
Created on Aug 7, 2011

@author: phil
'''
from SockServer.utils.ThreadUtil import synchronized, Synchronized
from socket import error,SHUT_WR
class BasicSocketHandler(Synchronized):
    ''' A Basic Class that handles accepted Connections for the SockServer or ThreadedSockServer
        This Class handles connected sockets
    '''

    def __init__(self):
        Synchronized.__init__(self)
        self._cfg={"loop":False}
        self._loop=True
        self._isClosed=False
        
        
    
    def isClosed(self):
        ''' True if disconnect() or doDisconnect was called'''
        return self._isClosed
    
    def handle(self):
        ''' The handle() method receives messages from a client and calls recv(msg) 
        '''
        con=self.getConnectionSocket()[0]

        try:
            r=con.recv(1024)
            if r != b"":
                self.recv(r)
            else:
                self.doDisconnect(True)
        except error:
            pass
        
    
    def recv(self,msg):
        ''' Is called each time the client sends a message to the server
            Basically you override this method
            Note that this method runs in a Loop in the TaskManager
            to avoid this, call doDisconnect() at the end of the method
            
            @param msg: A Bytestring with the Message 
        ''' 
        print(msg)
    
    def setup(self):
        ''' called after a successful connection'''
        pass
    
    def disconnected(self,reason):
        pass
    
    
    @property
    @synchronized
    def loop(self):
        ''' getter property for the external loop variable checked by the TaskManager'''  
        return self._loop
    
    
    @loop.setter
    @synchronized
    def loop(self,b):
        ''' setter property for the external loop variable'''  
        self._loop=b
    
    def config(self,**cfg):
        ''' configure parameter called before delegating to a TaskManager
            @param **cfg: a config dict  
        '''
        
        self._cfg.update(cfg)
    
    def getConnectionSocket(self):
        ''' @return: (socket,adress)'''
        
        return self._cfg["con"]
    
    @property
    def client(self):
        '''@return: The socket for this connection'''
        
        return self.getConnectionSocket()[0]
    
    def doDisconnect(self,foreign=False):
        ''' tells the TaskManager to stop the loop and disconnects the socket'''
        if self.isClosed():return
        self.loop=False
        try:
            
            if "taskmanager" in self._cfg:
                try:
                    self._cfg["taskmanager"].clients.remove(self.client)
                except Exception:
                    pass
                
            
            
            self.client.shutdown(SHUT_WR)
            self.client.close()
            
            
            if foreign:
                self.disconnected("foreign host closed connection")
            else: 
                self.disconnected("Server closed connection")
        except Exception as e:
            print("Error occured during socket close operation: ",e)
            
        
        self._isClosed=True