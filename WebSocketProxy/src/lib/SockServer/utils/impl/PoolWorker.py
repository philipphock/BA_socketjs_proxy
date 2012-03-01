'''
Created on Aug 8, 2011

@author: phil
'''
from threading import Thread
from queue import Empty

class PoolWorker(Thread):
    """Thread executing callable tasks from a given tasks queue"""
    def __init__(self, tasks,num,pool):
        Thread.__init__(self)
        self.tasks = tasks
        self.pool=pool
        self.num=num
        self.daemon = True
        self.start()
        
    
    def run(self):
        
        while True:
            
            if self.pool.isDead():
                break
            try:
                c_obj = self.tasks.get(True,1)
            except Empty:
                continue
            #print("worker busy")
            self.pool.push()
            c_obj.setup()
            while c_obj.loop:
                if self.pool.isDead():
                    c_obj.doDisconnect()
                else:
                    c_obj.handle()
            #print("worker free")
            self.pool.pop()
            self.tasks.task_done()
            del c_obj
        #print("worker dead")