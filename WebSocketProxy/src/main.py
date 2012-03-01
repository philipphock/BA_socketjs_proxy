'''
Created on 17.09.2011

@author: phil
'''

import sys
sys.path.append("lib")
from SockServer.impl.DynamicThreadPoolTaskManager import DynamicThreadPoolTaskManager
from SockServer.ThreadedSockServer import ThreadedSockServer
 

from SockServer.SockServer import SockServer
from SockServer.utils.SocketMode import SocketModeFactory

from config.Config import StdConfig, Log
    
import os
import socket
from security.PolicyControl import PolicyControl
from threading import Thread

from security.Authentication import Authentication
from websocket.proxy.WebSocketProxyHandler import WebSocketProxyHandler
from xml.etree.ElementTree import ParseError
from control.ControlInterface import ControlInterface

class InputThread(Thread):
    def __init__(self,exit_,cmd):
        Thread.__init__(self)
        self.setDaemon(True)
        self.exit=exit_
        self.cmd=cmd
    def run(self):
        while True:
            try:
                i=input("ctrl+D to exit: \n")
                if hasattr(self.cmd, '__call__'):
                    self.cmd(i)

            except Exception as e:
                if hasattr(self.exit, '__call__'):
                    self.exit() 
                break

def bootstrap():
    def cmd(cmd):
        print("cmd",cmd)
        
    def exit_():
        print("exit keystroke detected...")
        s.stop()        
        
    #generate folder structure
    pathlist=["../resources","../resources/logs"]
    for i in pathlist:
        if not os.path.exists(i):
            os.mkdir(i)
    
    #init config
    StdConfig.getInstance()
    
    try:
        policy=PolicyControl.getInstance()
    except ParseError as e:
        Log.error("Policy XML malformed")
         
    Authentication.init()
    proxyWSPort=StdConfig.getInstance().getProxyPort()
    adress=("localhost",proxyWSPort)
    
        
    #s=ThreadedSockServer(SocketModeFactory.TCP,DynamicThreadPoolTaskManager, WebSocketProxyHandler,policy.getMaxConnections())
    s=SockServer(SocketModeFactory.TCP, WebSocketProxyHandler,policy.getMaxConnections())
    if StdConfig.getInstance().isControlInterfaceEnabled():
        ci = ControlInterface(StdConfig.getInstance().getControlPort())
        ci.start()
    it=InputThread(exit_,cmd)
    s.setReuseAdress()
    try:
        s.bind(adress)
    except socket.error:
        Log.error("Socket could not be bound on port %s"%proxyWSPort)
        
    
    Log.info("websocket proxyserver started: %s"%(adress,))
    it.start()
    
    
    s.start()
    Log.info("websocket proxyserver stopped: %s"%(adress,))
    sys.exit(0)


if __name__ == '__main__':  
    bootstrap()  
    