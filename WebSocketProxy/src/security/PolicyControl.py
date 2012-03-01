'''
Created on 22.11.2011

@author: phil
'''
from config.Config import Log
from security.PolicyParser import PolicyParser
from security.PolicyData import Types, Policy, Policies
from security.AskPrompt import AskPrompt
from security.Authentication import Authentication

class PolicyControl(object):
    '''
    This class controls the outgoing javascript connections
    '''
    _instance=None
    
    
    def __init__(self):
        self.parser=PolicyParser("../resources/policies.xml")
        self.policies=self.parser.load()
        self._changelistener=None
        
    def setChangeListener(self,c):
        '''
            Observable method
        '''
        self._changelistener=c
        
    def updateGeneral(self,genDict):
        '''
            updates the general policies and writes down to file
            @param genDict: the policies as dict
        '''
        self.policies.unknownPolicyRule=genDict['unknownPolicyRule'].lower()
        
        self.policies.enabledSockets=Types(Types.TCP.lower() in genDict['enabledSockets'],Types.UDP.lower() in genDict['enabledSockets'],Types.UNIX.lower() in genDict['enabledSockets'])
        
        self.policies.localSource=genDict['localSource'].lower()
        self.policies.trustedSource=genDict['trustedSource'].lower()
        self.policies.trustedDest=genDict['trustedDest'].lower()
        
        self.policies.maxConnections=int(genDict['maxConnections'])
        
        self.parser.write(self.parser.toXML(self.policies))
    
    def addRule(self,policy):
        '''
            adds a Policy() and writes them down to file.
            also updates the Observer
        '''
        self.policies.addRule(policy)
        
        self.parser.write(self.parser.toXML(self.policies))
        try:
            self._changelistener.update()
        except:
            pass
        
    def removeRule(self,policy):
        '''
            removes a Policy() and writes them down to file
        '''
        self.policies.removeRule(policy)
        self.parser.write(self.parser.toXML(self.policies))
    
    
    def hasAccess(self,type_,src_,destination,auth):
        '''
        checks if the script has access 
        @param type_: TCP,UDP,UNIX
        @param src: the source url of the script [is null if local]
        @param destination: the destination url/ip to connect to   
        @param auth:
        '''
        #Log.debug("checking policy: \n type: %s \n  src: %s \n dest: %s \n auth: %s"%(type_,src_, destination,auth))
        d_uri, d_port = Policies.splitURI(destination)
        src = src_.decode() 
        if src == "null":
            src = "localhost"
        incomingRequestPolicy = Policy("", d_uri, d_port,src, type_)
        

        #print(str(self.policies))
        matchcount=0
        matchaction = None
        for k,rule in self.policies.specificRules.items():
            if self.matches(rule,incomingRequestPolicy):
                if matchcount != 0 and matchaction != rule.action:
                    Log.warning("multiple rules with conflicting actions detected: %s"%k)
                    
                matchcount += 1
                matchaction = rule.action
                
        
        if matchaction != None:
            return self.__proceed(matchaction,incomingRequestPolicy)
        Log.debug("passed specific")    
                        
        
        #no specific rule found:
        #testing for:
        #    trustedSource
        #    trustedDest
        #    localSource
        #    general rule
        
        SALTLEN = 8 
        for authElem in auth:
            
            
            #    trustedSource
            if chr(authElem[0]) == "S":
                authString1 = Authentication.hash(b"", authElem[1:SALTLEN+1])[1].encode()
                if authString1 == authElem[SALTLEN+1:]:
                    #trusted source detected
                    Log.policycontrol("Sourcekey detected")
                    return self.__proceed(self.policies.trustedSource,incomingRequestPolicy,"sourcekey")
                    
            Log.debug("passed srckey")
            #    trustedDest
            if chr(authElem[0]) == "H":
                deststr = d_uri+":"+str(d_port)
                authString1 = Authentication.hash(deststr.encode(), authElem[1:SALTLEN+1])[1].encode()
                authString2 = Authentication.hash(d_uri.encode(), authElem[1:SALTLEN+1])[1].encode()
                if authString1 == authElem[SALTLEN+1:] or authString2 == authElem[SALTLEN+1:]:
                    Log.policycontrol("Hostkey detected")
                    return self.__proceed(self.policies.trustedDest,incomingRequestPolicy,"hostkey")
                    
        
        Log.debug("passed hostkey")    
        #    localSource
        if src == b"localhost":
            return self.__proceed(self.policies.localSource,incomingRequestPolicy)
        Log.debug("passed local")            
            
        #    general rule
        return self.__proceed(self.policies.unknownPolicyRule,incomingRequestPolicy)
        Log.debug("passed general")
        return False
    
    
    def __proceed(self,rule,p,sourcekey="n/a"):
        if rule == Policy.ALLOW: return True
        if rule == Policy.DENY: return False
        if rule == Policy.ASK:
            return AskPrompt.showAskDialog(p,self,sourcekey)    
    
    def tcpAllowed(self):
        '''
            @return True if tcp is enabled in General Policies 
        '''
        return Types.TCP in self.policies.enabledSockets
    
    def udpAllowed(self):
        '''
            @return True if udp is enabled in General Policies 
        '''
        return Types.UDP in self.policies.enabledSockets
    
    def unixAllowed(self):
        '''
            @return True if unix is enabled in General Policies 
        '''
        return Types.UNIX in self.policies.enabledSockets
    
    def getMaxConnections(self):
        '''
            @return the max. connections to the proxy, -1 if infinity. 
        '''
        return int(self.policies.maxConnections)
    
    @staticmethod
    def matches(policy,other):
        '''
             @return True if an incoming policy (other) matches a specific (policy)
             @param policy: the specific policy.
             @param other: the Policy generated from a request.
        '''
        #print("checking: ",self.action)
        
        b=True
        b &= other.type in policy.type 
        #print(" type:",self.type,other.type,b)
        
        b &= other.dest == policy.dest or policy.dest == "" 
        #print(" dest:",self.dest,other.dest,b)
        
        b &= other.port == policy.port or policy.port == 0 or policy.port == ""
        #print(" port:",self.port,other.port,b)
         
        b &= other.src == policy.src or policy.src == "" 
        #print(" src:",self.src,other.src,b)
        
        
        return b
    
    @staticmethod
    def getInstance():
        if PolicyControl._instance==None:
            PolicyControl._instance=PolicyControl()
        
        return PolicyControl._instance