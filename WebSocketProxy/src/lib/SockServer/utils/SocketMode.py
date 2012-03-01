'''
Created on Aug 7, 2011

@author: phil
'''

from socket import  SOCK_DGRAM, SOCK_STREAM, AF_INET
import socket

class SockMode(object):
    ''' A SockMode is basically a workaround for an Enumeration Object
        that instantiate a Socket specified by the SocketModeFactory 
    '''
    try:
        unixFlag=socket.AF_UNIX
    except AttributeError:
        unixFlag=None
    
    def __init__(self,function,mode):
        self.__function = function
        self.__mode = mode   
        
        
        
    
    def generateSocket(self,**arg):
        ''' @return: a Socket'''
        
        return self.__function(arg)
    

    def tcp(self,**arg):
        return socket.socket(AF_INET, SOCK_STREAM) 
    

    def udp(self,**arg):
        return socket.socket(AF_INET,SOCK_DGRAM) 
    
    def unix(self,**arg):
        return socket.socket(SockMode.unixFlag, SOCK_STREAM)
         
    def getMode(self):
        ''' @return: The Mode ['TCP', 'UDP', 'UNIX']'''
        return self.__mode     
     
class SocketModeFactory(object):
    '''
    Static Factory Class
    Defines which mode a SockServer should run
    '''
    TCP  = SockMode(SockMode.tcp,"TCP")
    UDP  = SockMode(SockMode.udp,"UDP")
    UNIX = SockMode(SockMode.unix,"UNIX")
    
    
    

 

