'''
Created on 17.09.2011

@author: phil
'''

from SockServer.utils.basic.MessageIdentifyProtocol import MessageIdentifyProtocol
import hashlib
import base64

from websocket.version13.WSFrame import WSFrame,    FrameHeaderIncomplete

class WebSocketHandler(MessageIdentifyProtocol):


    def __init__(self):
        MessageIdentifyProtocol.__init__(self,True,True,True)
        self._wsFrame=WSFrame()
        self._wsStartFrame=WSFrame()
        self._msgLen=0
        self._uri=b""

        
    

    def _recvHeader(self,bytes):
        '''
           @return: a tuple with 2 bytestrings and 1 boolean (headerPart,messagePart,headerSend)
           headerPart are bytes that are part of the header
           messagePart are bytes that are part of a message
           headerSend is True, if the header is complete
           
        '''
        
        self._wsFrame.setBytes(bytes)
         
        
        try:
            pStartIndex = self._wsFrame.getPayloadStartIndex()
            header=bytes[:pStartIndex]
            rest = bytes[pStartIndex:]
            self._wsFrame.getMaskKey()
            self._msgLen=self._wsFrame.getPayloadLen()
            return (header,rest,True)    
        except FrameHeaderIncomplete:
            return (bytes,b"",False)
        

    def sendWSFrame(self,payload):
        self.rawSend(WSFrame.generateResponseFrame(payload))
        
    
    def _recvMessage(self,bytes):
        '''
           @return: a tuple with 2 bytestring and one boolean (c_message,o_messages,cmDone)
           c_message are bytes that are part of the current message
           o_message are bytes that are part of other messages
           cmDone is True if the current message is complete
        '''
        
        pl=self._wsFrame.getPayloadLen()
        
        return (bytes[:pl],bytes[pl:],len(bytes)>=pl)
        

    
    def _recvHandshake(self,bytes):
        '''
           @return: a tuple with 2 bytestrings and 1 boolean (handshakePart,restPart,handshake complete)    
        '''
        httpHeaderSeparatorPosition = bytes.find(b"\r\n\r\n")
        if httpHeaderSeparatorPosition == -1:
            return (bytes,b"",False)
        else:
            return (bytes[:httpHeaderSeparatorPosition],bytes[httpHeaderSeparatorPosition+4:],True)
        
  
    
    def aMessage(self,message):
        pass
        
    def aHeader(self,header):
        
        pass

    
        
    def aHandshake(self,handshake):
        try:
            headerLines=handshake.rsplit(b"\r\n")
            
            if not headerLines[0].startswith(b"GET /"):
                self.resetState()
                self.doDisconnect()
                return
            
            
            
            if b"\n" in headerLines[0]: #malformed request, prevent evil Header manipulations 
                self.resetState()
                self.doDisconnect()
                return
            
            end=headerLines[0].rfind(b" ")
            self.uri = headerLines[0][5:end]
            
            handshakeDict = {}
            for kv in headerLines:
                dbl=kv.find(b":")
                if dbl>0:
                    handshakeDict[kv[:dbl]]=kv[dbl+1:].lstrip()
    
            self.requestHeader=handshakeDict        
            if not handshakeDict[b"Sec-WebSocket-Version"]==b"13":
                self.resetState()
                self.doDisconnect()
                
            self.handshakeSuccessful(self.generateResponseHeader(handshakeDict),handshakeDict[b'Sec-WebSocket-Protocol'])
        except Exception as e:
            #self.errorMessage(b"unable to establish a socket tunnel")
            #print("error on establishing connection: ",e)
            self.resetState()
            self.doDisconnect()
            #raise e
    
    def handshakeSuccessful(self,respHeader,protocol):
        self.rawSend(respHeader)
            
    
    def generateResponseHeader(self,header):
        def generateAcceptChallenge(secWebSocketKey):
            hash = hashlib.sha1()
            hash.update(secWebSocketKey+b"258EAFA5-E914-47DA-95CA-C5AB0DC85B11")
            hash = hash.digest() 
            ret=base64.b64encode(hash)
            return ret
        
        resp=b"HTTP/1.1 101 Switching Protocols\r\n"
        resp=b"".join([resp,b"Upgrade: websocket\r\n"])
        resp=b"".join([resp,b"Connection: Upgrade\r\n"])
        resp=b"".join([resp,b"Sec-WebSocket-Accept: "+generateAcceptChallenge(header[b'Sec-WebSocket-Key'])+b"\r\n\r\n"])
        
        return resp
