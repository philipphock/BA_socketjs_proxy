'''
Created on 30.08.2011

@author: phil
'''
from SockServer.utils.basic.BasicSocketHandler import BasicSocketHandler

from threading import Thread
import time 


class RTimer(Thread):
    


    def __init__(self,repeatEvery,callback):
        Thread.__init__(self)
        self._r=repeatEvery
        self._c=callback
        self.setDaemon(True)
        self._loop=True
    
    def run(self):
        while self._loop:
            self._c(self)
            time.sleep(self._r)
        
    def stop(self):
        self._loop=False

        
class MessageIdentifyProtocol(BasicSocketHandler):
    '''
    A Baseclass that provides an interface that allows you to identify and separate different messages
    Also additional method stubs for a header are given.   
    
    Implement _recvHeader(self,header) and _recvMessage(self,msg) to multiplex between header and message and other messages
    '''

    

    def __init__(self,enableHeader=False,expectNewHeaderAfterEachMessage=False,handsake=False,keepAliveTimeout=0):
        BasicSocketHandler.__init__(self)
        self._handshake=b""
        self._handShaken=not handsake
        self._headerSend=not enableHeader
        
        self._rESEThandShaken=not handsake
        self._rESETheaderSend=not enableHeader
        
        self._expectNewHeaderAfterEachMessage=expectNewHeaderAfterEachMessage
        self._headerBytes=b""
        self._messageBytes=b''
        self._alvTimeout=keepAliveTimeout
        self._timeoutExpired=keepAliveTimeout
        
        if keepAliveTimeout > 0:        
            self._alvTimer=RTimer(1,self.keepAliveTimerEvent)
            self._alvTimer.start()
    
    def keepAliveTimerEvent(self,timer):
        if self._timeoutExpired <=0:
            timer.stop()
            self.doDisconnect()
        else:
            self._timeoutExpired-=1
    
    def keepAlive(self):
        self._timeoutExpired=self._alvTimeout
 
    def aMessage(self,message):
        ''' this method is called if a complete message is identified'''
        #print("message:",message)
    
    def aHeader(self,header):
        ''' this method is called if a complete header is identified'''
        #print("header:",header)
        
    def aHandshake(self,handshake):
        ''' this method is called if a complete handshake-header is identified'''
        #print("handshake")
    
    def recv(self,bytes):
        #print("rawIn: ",len(bytes),str(bytes))
        self.keepAlive()
        if not self._handShaken:
            sh,o,shn=self._recvHandshake(self._handshake+bytes)
            self._handshake=sh;
            if shn:
                self._handShaken=True
                self.aHandshake(self._handshake)
                if o is not b"":
                    self.recv(o)
            return
            
        if not self._headerSend:
            h,m,complete=self._recvHeader(self._headerBytes+bytes)
            self._headerBytes=h
            if complete:#header send and message part
                self._headerSend=True
                self.aHeader(self._headerBytes)
                if m is not b"":
                    self.recv(m)#recursive call to process other messages 
                    return
            else:#header not complete
                return
                
        else:#header send
            c,o,d=self._recvMessage(self._messageBytes+bytes)
            self._messageBytes=c
            if d:#c_message done (o must be empty)
                self.aMessage(self._messageBytes)
                self._messageBytes=b""
                if self._expectNewHeaderAfterEachMessage:
                    self._headerSend=False
                    self._headerBytes=b""
                if o is not b"":
                    self.recv(o)#recursive call to process other messages
                    return
            else:#message not complete
                pass
                
                   
    def _recvHeader(self,bytes):
        '''
           @return: a tuple with 2 bytestrings and 1 boolean (headerPart,messagePart,headerSend)
           headerPart are bytes that are part of the header
           messagePart are bytes that are part of a message
           headerSend is True, if the header is complete
           
        '''
        raise NotImplementedError
    
    def _recvMessage(self,bytes):
        '''
           @return: a tuple with 2 bytestring and one boolean (c_message,o_messages,cmDone)
           c_message are bytes that are part of the current message
           o_message are bytes that are part of other messages
           cmDone is True if the current message is complete
        '''
        raise NotImplementedError

    def _recvHandshake(self,bytes):
        '''
           @return: a tuple with 2 bytestrings and 1 boolean (handshakePart,restPart,handshake complete)    
        '''
        raise NotImplementedError
    
    def rawSend(self,msg):
#        print("rawOut: "+str(msg))
        self.client.send(msg)
        
    def resetState(self):
        self._headerBytes=b""
        self._messageBytes=b''
        self._handShaken=self._rESEThandShaken
        self._headerSend=self._rESETheaderSend
        
        
        