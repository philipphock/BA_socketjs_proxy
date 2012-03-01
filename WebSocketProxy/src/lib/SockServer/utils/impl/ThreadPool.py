'''
Created on Aug 8, 2011

@author: phil
'''
from SockServer.utils.basic.BasicTaskManager import BasicTaskManager

from queue import Queue
from SockServer.utils.ThreadUtil import synchronized

from SockServer.utils.impl.PoolWorker import PoolWorker



class ThreadPool(BasicTaskManager):
    ''' A ThreadPool implementation
        with interfaces to the SockServer to run as TaskManager
    '''

    def __init__(self,ch,serv,num_threads=5):
        BasicTaskManager.__init__(self,None,None,num_threads)
        
        
        def workerList(self):
            for i in range(num_threads):
                yield PoolWorker(self._tasks,i,self)
            
        self._tasks = Queue(num_threads)
        self._worker =[w for w in workerList(self)]
        
    @synchronized  
    def add_task(self,callable):
        self._tasks.put(callable)    


    def join(self):
        for w in self._worker:
            w.join()

    def info(self):
        pass