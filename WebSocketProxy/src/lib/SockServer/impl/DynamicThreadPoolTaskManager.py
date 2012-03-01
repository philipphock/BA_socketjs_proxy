'''
Created on Aug 8, 2011

@author: phil
'''
from SockServer.utils.basic.BasicTaskManager import BasicTaskManager,\
    configMethod, TaskManagerFullException

from SockServer.utils.ThreadUtil import synchronized
from SockServer.utils.impl.ThreadPool import ThreadPool
import math


class DynamicThreadPoolTaskManager(BasicTaskManager):
    ''' a TaskManager implementation with limited connections 
        This class uses ThreadPool to manage the SocketHandler
        and creates new ThreadPools, if all Workers in the Pool are busy
        If the maximum amount of ThreadPools is instantiated and full, the TaskManager serves no more incoming connections 
    '''
    
    def __init__(self,_,server,max):
        ''' @param server: the server
        ''' 
        BasicTaskManager.__init__(self,_,server,max)
        self._tpoolWorkerCount=0
        self._threadPools=0
        self._tpools=None
        if max<0:
            poolcount=64
        else:
            poolcount=math.ceil(max/64)
        self.setThreadParameter(64,poolcount)
        self._maxCon = max
        self._info=TaskManagerInfo(self)
        

    @property
    def info(self):
        ''' @return: an Info Object'''
        return self._info
    
        
    @configMethod
    def setThreadParameter(self,workerCount,poolCount):
        '''
            @param: workerCount {int} the number of workers in each pool
            @param: poolCount {int} the number of pools that can be created
            
            specify the amount of ThreadPools and WorkerThread for each Pool
            E.g. setThreadParameter(5,128) means that the TaskManager can create 128 ThreadPools each with 5 Workers
            Note: The TaskManager will not reschedule the Worker to other pools but tries to instantiate as less as possible pools  
        '''
        self._tpoolWorkerCount=poolCount
        self._threadPools=workerCount
        if self._num>poolCount*workerCount:
            self._num=poolCount*workerCount
        self._tpools=[]
        self._tpools.append(ThreadPool(None,None,self._tpoolWorkerCount))
        self._configured=False
        
    @synchronized    
    def getPool(self):
        ''' @return: a ThreadPool with the highes count of busy workers, or a new Pool if all pools a busy
            @raise TaskManagerFullException: if the connection limit is reached
        '''  
        self._tpools.sort()
        self._tpools.reverse()
        
        i=0
        ret=0
        
        for p in self._tpools:
            if p.isFull():#look for free pool
                ret+=1
            if(p.getSize()==0 and i>0):#no busy worker, delete pool
                tmpArray=self._tpools[i:]
                while len(tmpArray)>0:
                    tmpPool=tmpArray.pop()
                    tmpPool.die()
                    
                del self._tpools[i:]
                
            i+=1
        
        if(ret==len(self._tpools)):
            if len(self._tpools)>=self._num:
                raise TaskManagerFullException
            
            w=ThreadPool(None,None,self._tpoolWorkerCount)
            self._tpools.append(w)
            return w
        return self._tpools[ret]        


    def die(self):
        BasicTaskManager.die(self)
        for p in self._tpools:
            p.die()

    def join(self):
        for l in self._tpools:
            l.join()
        
    @synchronized  
    def add_task(self,task):
        if self._maxCon>-1 and self.getSize() >= self._maxCon:
            task.setup()
            task.handle()
            task.doDisconnect()
            return
        
        self.getPool().add_task(task)


    def getSize(self):
        ''' @return: the amount of busy workers in all Pools''' 
        size = 0
        for l in self._tpools:
            size+=l.getSize()
        return size


class TaskManagerInfo(object):
        ''' An info object for this ThreadPoolTaskManager'''
        def __init__(self,parent):
            self._parent=parent
            
        def info(self):
            ''' @return: InfoString'''
        
            freePool=self._parent._threadPools-len(self._tpools)
            i="__THREADPOOL INFO__\n"
            
            i+="PoolQueue len: "+str(len(self._tpools))+"\n"
            i+="Free Pool Slots: "+str(freePool)+"\n\n"
            i+=ThreadPool.info()
            i+="_________________\n"
            open=0
            
            for p in self._tpools:
                i+=str(p)+"\n"
                open+=p.getSize()
            
            max=self._parent.getCapacity()
            
            
            i+="\n__________________\n"
            i+="Max  Workers: %i\n"%max
            i+="Busy Workers: %i\n"%open
            i+="Free Workers: %i\n"%(max-open)
            i+="____________________\n\n"
        
        