'''
Created on Aug 8, 2011

@author: phil
'''


from SockServer.utils.impl.LimitedCapacity import LimitedCapacity
from SockServer.utils.ThreadUtil import synchronized


def configMethod(m):
        '''config method decorator
           Each method decorated with this function will raise an error 
           if called after init()
           this will prevent calling an setup method after it should not called
        '''
    
        def wrap(self,*varg,**darg):
            if self.isConfigured:
                raise ObjectAlreadyConfiguredException
            else:
                
                m(self,*varg,**darg)
             
        return wrap

class ObjectAlreadyConfiguredException(Exception):
    pass

class TaskManagerFullException(Exception):
    pass



class BasicTaskManager(LimitedCapacity):
    ''' A BaseClass for a TaskManager
    '''

    def __init__(self,ConnectionHandler,server,max=-1):
        ''' @param ConnectionHandler: if the TaskManager instantiates the ConnectionHandler, this variable is needed
                   The NonThreaded SockServer uses this variable
            @param max: the maximum of connections accepted by the TaskManager (a manual implementation is needed for this feature)
            
        '''
        LimitedCapacity.__init__(self,max)
        self._isDead=False#
        self._configured=False
        self._server=server
        self._connectionHandler=ConnectionHandler

    
    @property
    def isConfigured(self):
        ''' @return: True after the server is started and a configuration would lead to an ObjectAlreadyConfiguredException'''
        return self._configured

    def init(self):
        ''' initialization method for the server
            Do not override, if you have to configure the TaskManager, use config(**arg) method
        '''
        
        self._configured=True
    
    @synchronized
    def add_task(self,task):
        """Add a callable object to the TaskManager"""
        raise NotImplementedError
        
    @synchronized    
    def isDead(self):
        ''' @return: True if the TaskManager is dead an all its tasks or worker should stop'''
        return self._isDead

    @synchronized
    def die(self):
        ''' to stop the TaskManager an all its worker and sockets'''
        self._isDead=True
    
    @configMethod
    def config(self,**arg):
        ''' configuration method for the server.
            Note: do not call this method after the servers start method is called,
            it would lead to a ObjectAlreadyConfiguredException!
        '''
        pass