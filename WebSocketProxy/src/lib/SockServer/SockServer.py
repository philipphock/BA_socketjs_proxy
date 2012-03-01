'''
Created on Aug 7, 2011

@author: phil
'''
import select

from SockServer.utils.basic.BasicSockServer import BasicSockServer
from SockServer.utils.basic.BasicTaskManager import BasicTaskManager

import socket as socket_p
import socket




class SockServer(BasicSockServer):
    ''' A non threaded SocketServer derived from the BasicSockServer
        This implementation uses a Select method and a modified TaskManager to demultiplex the Sockets
        Use this Server for a low resource implementation with limited connections
    '''
    
    def __init__(self,SocketMode, ConnectionHandler, max_con=-1):
        BasicSockServer.__init__(self, SocketMode, NonThreadedTaskManager, ConnectionHandler, max_con)
#        t=RTimer(10,self.status)
#        t.start()
        
#    def status(self,t):
#        print(len(self._taskManager.clients))

    def start(self):
        self._taskManager.init()
        
        try:
            while self._loop:
                read,_,_ = select.select([self.socket]+self._taskManager.clients,[],[])
                try:
                    self.accept(read)
                except socket_p.error:
                    pass
        finally:
            self._close()


            
    def accept(self,con):
        for r in con:
            self._taskManager.demux(r)





class NonThreadedTaskManager(BasicTaskManager):
    ''' A special modified TaskManager with demultiplexing functions
        used by the non threaded SockServer
    '''
    def __init__(self,ConnectionHandler,server,max_con=-1,autokick=True):
        BasicTaskManager.__init__(self,ConnectionHandler, server, max_con)
        self._clients=[]
        self._handlers={}
        self._socket=server.socket
        self._dieHandler=[]
        self._autokick=autokick
        
    @property
    def clients(self):
        return self._clients

    def demux(self,r):
        ''' Each Connection could be an accept from the ServerSocket or 
            a connection with an already connected socket
            This method decides which one and delegates to the correct handler 
        '''

        if(r == self._socket):#new connection
            curCon=len(self._clients)
            con = self._socket.accept()
            
            if curCon==self.getCapacity():#full
                if self._autokick:
                    self._handlers[(self.clients.pop(),)].doDisconnect()
                    self._clients.append(con[0])
                    h=self._handle((con[0],))
                else:
                    con[0].close()
            else:
                self._clients.append(con[0])
                h=self._handle((con[0],))
        else:#input
            h=self._handle((r,))        
            if h.isClosed():
                try:
                    self._clients.remove(r)
                except ValueError:
                    pass
                
        
    
    def _handle(self,connection):
        if connection not in self._handlers:
            
            h = self._connectionHandler.__new__(self._connectionHandler)
            h.__init__()
            self._handlers[connection] = h 
            h.config(socket=self._socket,con=connection,server=self._server,taskmanager=self)
            h.setup()
                        
        h=self._handlers[connection]     
        if not h.isClosed():
            h.handle()
        return h 
        
        
        
    def die(self):
        for c in self._clients: 
            c.shutdown(socket.SHUT_RD)
            c.close() 
            
        
        
    def config(self,**args):
        self._autokick=args['autokick']
        
        
        
        
