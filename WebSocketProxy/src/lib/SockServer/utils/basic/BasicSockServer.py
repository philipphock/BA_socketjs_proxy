'''
@author: phil
'''

from socket import SHUT_RDWR,  error
try:
    from IN import SOL_SOCKET, SO_REUSEADDR
except ImportError:
    from socket import SOL_SOCKET, SO_REUSEADDR
from SockServer.utils.basic.BasicTaskManager import TaskManagerFullException
import os



class BasicSockServer(object):
    ''' A Basic Socket Server
        Accepts incoming Connections and delegates is to the accept(connection) method
        Override the accept(connection) method to implement a Server 
        Note: You have to define a TaskManager or override the start method for proper work
    '''

    def __init__(self,SocketMode,TaskManager,ConnectionHandler,max_con=-1):
        ''' 
            @param SocketMode: define what kind of Socket the Server uses. Use the SocketModeFactory
            @param TaskManager: The TaskManager for scheduling the accepted connections. Use a Class here, not an instance 
            @param ConnectionHandler: Each accepted connection is handled by the ConnectionHandler. Use a Class here, not an instance
            @param max_con: a parameter for the TaskManager to limit the connections  
            
        '''
        self._socket = SocketMode.generateSocket()
        self._loop=True
        self._taskManager=TaskManager.__new__(TaskManager)
        self._taskManager.__init__(ConnectionHandler,self,max_con)
        self._connectionHandler=ConnectionHandler
        self._prop={}
        
        
    def addProperty(self,key, value):
        self._prop.update({key:value})

    def getProperties(self):
        return self._prop
                
    def setReuseAdress(self):
        ''' call this method to reuse the socket immediately after it was closed
            do not call this method after bind oder start 
        '''
         
        self._socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

    @property
    def taskManager(self):
        ''' @return: TaskManager instance'''
        return self._taskManager
        
    def bind(self,connection):
        ''' binds the socket to the specific connection
            @param connection: (host,port) OR "unixSocketPath" 
            
        ''' 
        if(type(connection)==type("")):
            #unix socket
            try:
                os.remove(connection)
            except OSError:
                pass

        self._socket.bind(connection) 
        
        self._socket.listen(1)
        
            
       
    def stop(self):
        ''' shuts down the server'''
        self._loop=False
        self._socket.shutdown(SHUT_RDWR)
        
    
    def _close(self):
        self._socket.close()
        self._taskManager.die()
        
        
    def start(self):
        ''' starts the server an calls accept(connection) after the socket accepts an incoming connection
            Note that this method runs in a loop until doClose() is called
        '''
        self._taskManager.init()
        try:
            while self._loop:
                try:
                    con = self._socket.accept()
                except error:
                    break
                lock=self.taskManager.lock
                lock.acquire()
                try:
                    self.accept(con)
                except TaskManagerFullException:
                    con[0].shutdown(SHUT_RDWR)
                    con[0].close()
                lock.release()
        finally:
            self._close()

    def accept(self,con):
        raise NotImplementedError

    @property
    def socket(self):
        ''' @return: the Socket'''
        return self._socket
    
