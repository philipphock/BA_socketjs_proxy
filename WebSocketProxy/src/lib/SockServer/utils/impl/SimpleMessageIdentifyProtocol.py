'''
Created on 30.08.2011

@author: phil
'''
from SockServer.utils.basic.MessageIdentifyProtocol import MessageIdentifyProtocol

class SimpleMessageIdentifyProtocol(MessageIdentifyProtocol):
    ''' a simple MessageIdentifyProtocol:
        each message has a header that contains only the length of the payload
        the header is separated by a b":", e.g.
        12:hello world!3:bye is:
        hello world!
        bye
        
        the protocol also implements a handshake:
        the first 4 bytes in this connection must be b"CNTD" to allow a bidirectinal communication 
        
    '''
    def __init__(self,handshake=True,keepAlive=60):
        MessageIdentifyProtocol.__init__(self, True, True,handshake,keepAlive)
        
    def _recvHeader(self,bytes):
        dbloffset= bytes.find(b":")
        if dbloffset == -1:#no : found => header unfinished:
            try:
                int(bytes)
            except ValueError:
                self.doDisconnect()
            return (bytes,b"",False)
    
        return (bytes[:dbloffset],bytes[dbloffset+1:],True)
    
    def _recvMessage(self,bytes):
        try:
            cmsgLen = int(self._headerBytes)
        except ValueError:
            #header unreadable:
            self.doDisconnect()
            return (b"",b"",False)
        
        if len(bytes) >= cmsgLen:#c_msg send
            return (bytes[:cmsgLen],bytes[cmsgLen:],True)
        else: return (bytes,b"",False)

    def _recvHandshake(self,h):
        if len(h) >= 4:
            if h[0:4]==b"CNTD": 
                #self.toClient(b"CNTD")
                self.rawSend(b"CNTD")
                return (h[0:4],h[4:],True)
            else:
                self.doDisconnect()
                return (b"",b"",False)
        else:
            return (h,b"",False)

    

    def toClient(self,msg):
        leng=str(len(msg))
        self.rawSend(bytes(leng,encoding='ascii')+b":"+msg)
    
    