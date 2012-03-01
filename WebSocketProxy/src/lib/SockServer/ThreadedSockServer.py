'''
Created on Aug 7, 2011

@author: phil
'''
from .utils.basic.BasicSockServer import BasicSockServer



class ThreadedSockServer(BasicSockServer):
    ''' A ThreadedSockServer
        Example Usage:
        ss = ThreadedSockServer(SocketModeFactory.TCP, DynamicThreadPoolTaskManager, EchoSockHandler,2)
        ss.taskManager.setThreadParameter(1,2)
        ss.setReuseAdress()
        ss.bind(("localhost",6666))
        ss.start() 
    '''
    def __init__(self,socketMode,TaskManager,connectionHandler,max_con=-1):
        BasicSockServer.__init__(self,socketMode,TaskManager,connectionHandler,max_con)
        
  
        
        
        
    
    def accept(self,con):
        handler=self._connectionHandler.__new__(self._connectionHandler)
        handler.__init__()
        handler.config(socket=self._socket,con=con,server=self)
        self._taskManager.add_task(handler)
        
        