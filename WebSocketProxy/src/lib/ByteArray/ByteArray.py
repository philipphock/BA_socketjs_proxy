import operator
class ByteArray(bytearray):
    class BitOperation(object):
        def __init__(self,parent):
            self._parent=parent
        
        
        def bitIndex(self,pos):
            '''
            @return bitIndex, byteIndex
            '''
            bitIndex=(pos%8)
            byteIndex=int(pos/8)
            return bitIndex, byteIndex

        def __setitem__(self,k,v):
            if len(v)>1:
                for i in range(len(v)):
                    self[k+i]=v[i]
                return
            bitIndex, byteIndex = self.bitIndex(k)

            if len(self._parent)<=byteIndex:
                byte=0
            else:
                byte=self._parent[byteIndex]
                
            if v=="0":
                bitMask = ~(1<<(7-bitIndex))
                byte=byte&bitMask
            else:
                bitMask = 1<<(7-bitIndex)
                byte=byte|bitMask
            self._parent[byteIndex]=byte


        def __delitem__(self,v):
            s=str(self)
            sub=s[:v]+s[v+1:]
            self[0]=sub

        def __getSliceValues(self,key):
            start=key.start
            stop=key.stop
            step=key.step
            if start==None:
                start=0
            if stop==None:
                stop=len(self._parent)*8
            if step==None:
                step=0  
            return start,stop,step
        
        
        def __len__(self):
            return len(self._parent)*8
        
        def __getitem__(self,key):
            if type(key) != type(0):
                start,stop,_=self.__getSliceValues(key)
                return self.__getBits(start,stop-start)
            
            bitIndex, byteIndex=self.bitIndex(key)
            bit=(self._parent[byteIndex]>>(7-bitIndex)) & 1 
            return str(bit)
        
        def __getBits(self,start,len=1):
            bits=""
            for b in range(start,start+len):
                bits+=self[b]
            return bits
                   
        def __str__(self):
            return self[:]
    

        
    def __init__(self,bytes=b""):
        bytearray.__init__(self,bytes)
        self.bitOperation=ByteArray.BitOperation(self)
    
    def toDecimal(self):
        ret=0
        cnt=0
        for i in range(len(self.bitOperation)-1,-1,-1):
            if self.bitOperation[i] == "1":
                ret+=2**(cnt)
            cnt+=1 
        return ret
    
    def clear(self):
        while len(self)>0:
            del self[0]
   
    def __xor__(self,other):
        return self.__eachOperation2(other, operator.xor)
    
    def __and__(self,other):
        return self.__eachOperation2(other, operator.add)
    
    def __or__(self,other):
        return self.__eachOperation2(other, operator.or_)
    

    def __eachOperation2(self,other,operator):
        ret,min=self.__min(other)
        for i in range(min):ret[i]=operator(self[i],other[i])
        return ret

    def __eachOperation1(self,operator):
        ret,min=self.__min()
        for i in range(len(self)):ret[i]=operator(self[i])
        return ret
    
        
    def __min(self,*other):
        ls=len(self)
        lens=[len(i) for i in other]+[ls]
        min=ls
        for l in lens:
            if l<min:min=l
        
        if min==0:min=1
        return ByteArray(b"x00"*(min-1)),min
    
    def __setitem__(self,k,v):
        if type(v)==type(b""):
            for i in range(len(v)):
                self[k+i]=v[i]
            return
    
        leng=(k+1)-len(self)
        for _ in range(leng):self.append(0)     
        bytearray.__setitem__(self,k,v)

    

