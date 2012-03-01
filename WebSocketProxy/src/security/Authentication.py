'''
Created on Nov 28, 2011

@author: phil
'''
from ByteArray.ByteArray import ByteArray
from random import randint
import hashlib
import os

from config.Config import Log
import binascii
class Authentication(object):
    '''
        Class that provides static helper Methods for the Authentication 
    '''
    keyPath="../resources/security.token"
    
    @staticmethod
    def init():
        if not os.path.exists(Authentication.keyPath):
            Log.warning("security token does not exist, generating new random value")
            Authentication.key=Authentication.generateRandomBytes(2048)
            with open(Authentication.keyPath,"wb") as f:
                f.write(Authentication.key)

        else:
            
            with open(Authentication.keyPath,"rb") as f:
                Authentication.key=f.read()
            
        pass

    @staticmethod
    def generateRandomBytes(length):
        '''
            this static method generates a random bitstring
            @param length: the length of the bitstring in byte 
        '''
        ret = ByteArray(bytes(length))
        for i in range(length):
            rnd=randint(0,255)
            ret[i]=rnd
        return ret
    
    @staticmethod
    def hash(val,salt=None,appendKey=True):
        '''
            creates a hashvalue with sha512 algorithm.
            @param val: bytes() to hash
            @param salt: append salt to hash
            @param appendKey: appends the server-key to the hash
            @return (salt,hash)    
        '''
        m = hashlib.sha512()
        
        m.update(val)
        if appendKey:
            m.update(Authentication.key)
        
        if salt is not None:
            m.update(salt)
            return (salt,m.hexdigest())
        
        return m.hexdigest()

    @staticmethod
    def generateSalt(len):
        '''
            @return a salt as HexString
            @param len: the length of the salt in byte, note that the retured value is 2*len because 2 Hex-Digits = 1 Byte 
        '''
        
        b=Authentication.generateRandomBytes(len)
        b=binascii.b2a_hex(b)
        return b
        
    
    @staticmethod
    def generateHostkey(host):
        '''
            @return new Hostkey
            @param host: Bytes() the hostname 
        '''
        return Authentication.hash(host, Authentication.generateSalt(4))

    @staticmethod
    def generateSourcekey():
        '''
            @return new Sourcekey 
        '''
        return Authentication.hash(b"",Authentication.generateSalt(4))

    
    

#with open("../../resources/security.token","rb") as f:
#    Authentication.key=f.read()
#print(Authentication.generateSourcekey())    
#print(Authentication.generateHostkey(b"localhost:6667"))

