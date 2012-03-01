'''
Created on Aug 8, 2011

@author: phil
'''
from SockServer.utils.ThreadUtil import synchronized, Synchronized



class ThreadPoolInfo(Synchronized):
    '''@deprecated'''
    _inst=0    
    _cnt=0

    def __init__(self,threadPool):
        Synchronized.__init__(self)
        self._threadPool=threadPool
        ThreadPoolInfo._cnt+=1
        ThreadPoolInfo._inst+=1
        self._busy=0

    @synchronized  
    def busy(self):
        self._busy+=1
        
        
    @synchronized    
    def free(self):
        self._busy-=1
        
        
    @synchronized
    def isBusy(self):
        '''needed for TaskManager function'''
        return self._busy==self._num
    
    @synchronized
    def getSize(self):
        return self._busy

    @synchronized
    def __del__(self):
        ThreadPoolInfo._inst-=1


    ## comparision ##
    def __eq__(self, other):
        return self.getSize()==other.getSize()

    def __lt__(self, other):
        return self.getSize()<other.getSize()

    def __ne__(self, other):
        return self.getSize()!=other.getSize()

    def __gt__(self, other):
        return self.getSize()>other.getSize()

    def __le__(self, other):
        return self.getSize()<=other.getSize()

    def __ge__(self, other):
        return self.getSize()>=other.getSize()
    
    def __str__(self):
        return "Pool "+str(self._id)+": "+str(self.getSize())+" busy workers, free slots:"+str(self._num-self.getSize()) 
    

        
    
    @staticmethod    
    def info():
        s=""
        s+="ThreadPools:\n"    
        s+=" current instances: "+str(ThreadPoolInfo._inst)+"\n"
        s+=" died: "+str(ThreadPoolInfo._cnt-ThreadPoolInfo._inst)+"\n"
        return s
