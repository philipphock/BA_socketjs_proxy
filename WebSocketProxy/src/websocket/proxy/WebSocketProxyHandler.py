'''
Created on 20.09.2011

@author: phil
'''
from websocket.version13.WebSocketHandler import WebSocketHandler
from SockServer.utils.SocketMode import SocketModeFactory
from threading import Thread
import base64
from security.PolicyControl import PolicyControl
from config.Config import Log
import socket



class WebSocketProxyHandler(WebSocketHandler):



    def __init__(self):
        WebSocketHandler.__init__(self)
        self._policyControl=PolicyControl.getInstance()
        
  
    def aMessage(self,msg):
        dec=self._wsFrame.decode(msg)
        dec=base64.b64decode(dec)      
        self.sockClient.send(dec)
        

    def incomingMessage(self,msg,a=None):
        msg=b"M"+base64.b64encode(msg)
        self.sendWSFrame(msg)
    

    
    def handshakeSuccessful(self, respHeader,c):
        c=list(map(lambda s: s.lstrip(),c.split(b",")))
        
        self._socketType = None
        if b"proxy" not in c:
            Log.error("An incoming connection has no proxy field",False)
            self.doDisconnect()
            return 
            
        self.uri=base64.b64decode(self.uri)
        if(b"TCP" in c):

            if self._policyControl.tcpAllowed():
                self._socket=SocketModeFactory.TCP.generateSocket()
                self._socketType="TCP"
            else:
                Log.policycontrol("An incoming tcp connection was rejected: TCP socket types disabled")
                self.doDisconnect()
                return
        
        if(b"UNIX" in c):
            if self._policyControl.unixAllowed():
                self._socket=SocketModeFactory.UNIX.generateSocket()
                self._socketType="UNIX"
            else:
                Log.policycontrol("An incoming unix connection was rejected: UNIX socket types disabled")
                self.doDisconnect()
                return
            
        if(b"UDP" in c):
            if self._policyControl.udpAllowed():
                self._socketType="UDP"
                self._socket=SocketModeFactory.UDP.generateSocket()
            else:
                Log.policycontrol("An incoming udp connection was rejected: UDP socket types disabled")
                self.doDisconnect()
                return
        
        if self._socketType is None:
            Log.warning("Incoming request has no socket specified")
            self.doDisconnect()
            return
        
        if self._socketType=="UNIX":
            uri=self.uri
            destination=uri
        else:
            port=self.uri[self.uri.rfind(b":")+1:]
            uri=self.uri[:self.uri.rfind(b":")]    
            destination=(uri,int(port))
        
        #policy control
        authStrings = list( filter(lambda elem: len(elem)>10 and ( chr(elem[0])=="H" or chr(elem[0])=="S") ,c)) 
        
        if self._policyControl.hasAccess(self._socketType,self.requestHeader[b'Origin'],destination, authStrings):
            self.connectRemote(destination,respHeader,c)
        else:
            Log.policycontrol("Access denied for: %s connection to %s"%(self._socketType,destination))
            self.doDisconnect(False)
        

    
    def disconnected(self, reason):
        Log.info("".join([str(self._socketType)," bridge closed for ",str(self.uri)," > ",reason]))
        if hasattr(self,"sockClient"): 
            self.sockClient.stop()
        WebSocketHandler.disconnected(self, reason)

    def connectRemote(self,connection,respHeader,c):
        if self._socketType=="UNIX":
            sc=SockClient(self._socket,self.uri,self)
        
        else:
            sc=SockClient(self._socket,connection,self)
        
            
        self.sockClient=sc
        sc.start()    
        WebSocketHandler.handshakeSuccessful(self, respHeader,c)
        Log.info("".join([str(self._socketType)," bridge established to ",str(self.uri)]))        


class SockClient(Thread):

    def __init__(self,socket,con,proxy):
        Thread.__init__(self)
        self.socket=socket
        self.setDaemon(True)
        self.socket.connect(con)
        self.proxy=proxy
    
    def packMessage(self,to,msg):
        if to is None:return msg #tcp
        if to[0] is 0:return msg
        
        if(self.proxy._socketType=="UNIX"): #unix
            return to.encode("UTF-8")+b"\n"+msg
        
        p=str(to[1]).encode("UTF-8") #udp
        a=to[0].encode("UTF-8")
        
        return a+b":"+p+b"\n"+msg    
    
    def stop(self):
        #shutdown if possible
        try:
            self.socket.shutdown(socket.SHUT_RD)
        except:
            pass
        
    def run(self):

        while not self.proxy.isClosed():
            data, addr = self.socket.recvfrom(65536)
            
            if not data:
                break
            self.proxy.incomingMessage(self.packMessage(addr, data))
        
        self.socket.close();
        self.proxy.doDisconnect();
        
    def send(self,msg):
        self.socket.send(msg)

