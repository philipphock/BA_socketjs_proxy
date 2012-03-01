'''
Created on 17.09.2011

@author: phil

'''

class WebSocketProtocolState(object):
    NOT_INITIALIZED = "NOT_INITIALIZED"
    HAND_SHAKEN = "HAND_SHAKEN"
     
    

class WebSocketProtocolInterface(object):
    
    
    def __init__(self):
        pass
    
    def recv(self,bytes):
        pass
    
    