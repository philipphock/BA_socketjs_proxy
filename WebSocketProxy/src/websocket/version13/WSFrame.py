'''
Created on 17.09.2011

@author: phil
'''
import struct
from ByteArray.ByteArray import ByteArray

class FrameHeaderIncomplete(Exception):
    pass
class WSFrame(object):

    @staticmethod
    def generateResponseFrame(payload):
        bytes=ByteArray()
        bytes.bitOperation[0]="100000010"
        leng=len(payload)
        
        if leng<126:
            bytes[1]=leng
        elif leng < 65536:
            bytes[1]=126
            bString=ByteArray(struct.pack(">H",leng))
            bString=str(bString.bitOperation)
            bytes.bitOperation[16]=bString
            
        else:
            bytes[1]=127
            bString=ByteArray(struct.pack(">Q",leng))
            bString=str(bString.bitOperation)
            bytes.bitOperation[16]=bString
            
        bytes=b"".join([bytes,payload])
        return bytes 
    
    
    def __init__(self):
        self._len=0
        pass
    
    def setBytes(self,bytes):
        '''
        set the bytes of the WebSocketFrame from an incoming data stream
          
        '''
        self._bytes=bytes
        self._len=len(bytes)
    
    def getFin(self):
        return (ByteArray(self._bytes)).bitOperation[0]
        
    
    def getOpcode(self):
        return (ByteArray(self._bytes)).bitOperation[4:8]
    
    def getMaskBit(self):
        return (ByteArray(self._bytes)).bitOperation[8]

    
    def getPayloadLen7(self):
        if self.getByteLen()<2:
            raise FrameHeaderIncomplete
        ba=ByteArray(self._bytes)
        ret=ByteArray()
        ret.bitOperation[1]=ba.bitOperation[9:16]
        i=ret.toDecimal()
        return i
            
    
    def getExtendedPayloadLen16(self):
        if self.getByteLen()<4:
            raise FrameHeaderIncomplete

        ba=ByteArray(self._bytes)
        ret=ByteArray()
        ret.bitOperation[0]=ba.bitOperation[16:32]
        i=ret.toDecimal()
        return i   
    
    def getExtendedPayloadLen64(self):
        if self.getByteLen()<10:
            raise FrameHeaderIncomplete
        ba=ByteArray(self._bytes)
        ret=ByteArray()
        ret.bitOperation[0]=ba.bitOperation[16:80]
        i=ret.toDecimal()
        return i    
    
    def getByteLen(self):
        return len(self._bytes)#self._len
    
    def getMaskKeyStartIndex(self):
        
        p=self.getPayloadLen7()
        if p == 126:
            if self.getByteLen() < 4: raise FrameHeaderIncomplete
            return 4
        elif p == 127:
            if self.getByteLen() < 10: raise FrameHeaderIncomplete
            return 10
        else:
            if self.getByteLen() < 2: raise FrameHeaderIncomplete
            return 2
        
    

    def getPayloadLen(self):
        p=self.getPayloadLen7()
        if p == 126:
            return self.getExtendedPayloadLen16()
        if p == 127:
            return self.getExtendedPayloadLen64()
        return p



    def getMaskKey(self):
        if self.getMaskBit()=="0":return 0
        try:
            i = self.getMaskKeyStartIndex()
        except IndexError:
            raise FrameHeaderIncomplete()
        if (self.getByteLen()<i+4):
            raise FrameHeaderIncomplete()
        m=self._bytes[i:i+4]
        return m
       
    def decode(self,bytes):
        ret=bytearray()
        key=self.getMaskKey()
        for i in range(len(bytes)):
            ret.append(bytes[i] ^ key[i % 4])
        return ret
    
    def getPayloadStartIndex(self):
        '''
        @return: -1 if no payload is contained
        a positive integer where the payload data begins
        '''
        add = (4 if self.getMaskBit() == "1" else 0)  
        m=self.getMaskKeyStartIndex()+add
        return m
            
    


    def __str__(self):
        try:
            s=str(self.getPayloadLen())
        except FrameHeaderIncomplete:
            s="unknown"
        return "WebSocketFrame: \n FrameLen: " +str(len(self._bytes))+ "\n PayloadLen: "+s+"\n Fin: "+self.getFin()+"\n Opcode: "+self.getOpcode()+" \n MaskedKey: "+str(self.getMaskKey())+" \nPayloadStarts at: "+str(self.getPayloadStartIndex())
    


    