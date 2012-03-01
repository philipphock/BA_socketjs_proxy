'''
@author: phil
'''
from threading import RLock
def synchronized(m):
        '''synchronized decorator'''
        def wrap(self,*varg,**darg):
            with self.lock:
                return m(self,*varg,**darg) 
        return wrap


class Synchronized(object):
    ''' adds a RLock() object and a lock() property to the Class'''
    def __init__(self):
        self._lock=RLock()
    
    @property
    def lock(self):
        return self._lock
    
    