'''
Created on Aug 8, 2011

@author: phil
'''
from SockServer.utils.ThreadUtil import Synchronized, synchronized

class LimitedCapacity(Synchronized):
    ''' A Class that specifies a Capacity'''
    

    def __init__(self,max,startValue=0):
        Synchronized.__init__(self)
        self._num=max
        self._busy=startValue
        
        

    @synchronized  
    def push(self):
        ''' increases the capacity by one''' 
        if self._busy!=self._num:
            self._busy+=1
            return True
        return False
        
        
    @synchronized    
    def pop(self):
        ''' decreases the capacity by one'''
        self._busy-=1
        
        
    @synchronized
    def isFull(self):
        ''' @return: True, if size==capacity'''
        return self.getSize()==self.getCapacity()
    
    @synchronized
    def getSize(self):
        ''' the size'''
        return self._busy

    
    def getCapacity(self):
        ''' the maximum'''
        return self._num
    

    ## comparision ##
    # overloading methods to compare, e.g. for sorting algorithms#
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

        