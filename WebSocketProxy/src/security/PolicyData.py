'''
Created on 23.11.2011

@author: phil
'''
from config.Config import Log


class PolicyAlreadyExistsException(Exception):
    def __init__(self):
        Exception.__init__(self)



class Policies(object):
    '''
        Entity Class for the Policies
    '''
    
    def __init__(self):
        self.unknownPolicyRule=Policy.ASK
        self.enabledSockets=Types()
        
        self.localSource=Policy.ASK
        self.trustedSource=Policy.ASK
        self.trustedDest=Policy.ASK
        
        self.specificRules={}
        self.maxConnections=-1
    
    def addRule(self,policy):
        
        if policy in self.specificRules:
            raise PolicyAlreadyExistsException
        
        Log.policycontrol("rule added %s"%str(policy))
        self.specificRules[str(policy)]=policy
        
    
        
    def removeRule(self,rule):
        if type(rule)==type(""):
            del self.specificRules[rule]
        elif type(rule)==type(Policy()):
            del self.specificRules[str(rule)]
        Log.policycontrol("rule removed %s"%str(rule))
    
    def __str__(self):
        s="POLICIES:\n"
        s+=" " + self.unknownPolicyRule + "UNKNOWN\n"
        
        
        
        s+=" ENABLED SOCKETS: "+str(self.enabledSockets)+"\n"
        
        s+=" localSource: %s \n"%self.localSource
        s+=" trustedSource: %s \n"%self.trustedSource
        s+=" trustedSource: %s \n"%self.trustedSource
        s+=" max connections: %i \n"%(self.maxConnections)
        for sr in self.specificRules:
            s+=" "+sr+"\n"
        return s

    @staticmethod
    def splitURI(uri):
        if uri == None: return None,None
        if type(uri) == type(b""):
            return uri.decode(),0
        return uri[0].decode(),int(uri[1])

class Types(object):
    '''
        Types represents the option, which connection is allowed or active.
        all combinations of [TCP,UDP,UNIX] are possible
    '''
    UDP="UDP"
    TCP="TCP"
    UNIX="UNIX"
    
    @staticmethod
    def all():
        return (Types.TCP,Types.UDP,Types.UNIX)
        
    def __init__(self,tcp=True,udp=True,unix=True):
        self.tcp=tcp
        self.udp=udp
        self.unix=unix
        
    def __str__(self):
        s=""
        if self.tcp: s+=" TCP "
        if self.udp: s+=" UDP "
        if self.unix: s+=" UNIX "
        return s

    def isUnix(self):
        '''
            @return True if Unix is enabled
        '''
        return bool(self.unix)
    
    def isTCP(self):
        '''
            @return True if TCP is enabled
        '''    
        return bool(self.tcp)
    
    
    def isUDP(self):
        '''
            @return True if TDP is enabled
        '''
        return bool(self.udp)
    
    def enableUNIX(self,enable=True):
        '''
            @param enable=True: enable/disable Unix
        '''
        self.unix=enable
        
    def enableTCP(self,enable=True):
        '''
            @param enable=True: enable/disable TCP
        '''
        self.tcp=enable
    
    def enableUDP(self,enable=True):
        '''
            @param enable=True: enable/disable UDP
        '''
        self.udp=enable

    def __contains__(self,key):
        ret=False
        ret|=(self.tcp and key == Types.TCP)
        ret|=(self.udp and key == Types.UDP)
        ret|=(self.unix and key == Types.UNIX)
        
        return ret;    
        
    def __iter__(self):
        for t in Types.all():
            if t in self:
                yield t
                
        
    
    
class Policy(object):
    '''
        Entity represents a specific policy
    '''
    ALLOW="allow"
    DENY="deny"
    ASK="ask"
    
    ANY=""
    
    def __init__(self,action="deny",dest="localhost",port=8080,src="",type=Types(True)):
        self.action=action
        self.dest=dest
        try:
            self.port=int(port)
        except:
            self.port=0
        self.src=src
        self.type=type
    
    
 
    
    def __str__(self):
        if self.type == Types.UNIX:
            return self.src+": "+self.action+" "+str(self.type)+": "+str(self.dest)
        return self.src+": "+self.action+" "+str(self.type)+": "+str(self.dest)+":"+str(self.port)

        
    

        
        
        

