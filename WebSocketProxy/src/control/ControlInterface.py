'''
Created on 20.11.2011

@author: phil
'''

from SockServer.SockServer import SockServer
from SockServer.utils.SocketMode import SocketModeFactory

from config.Config import Log, StdConfig
import socket,json
from SockServer.utils.impl.SimpleMessageIdentifyProtocol import SimpleMessageIdentifyProtocol
from security.PolicyData import Policy, Types
from threading import Thread
import base64
from security.PolicyControl import PolicyControl
import functools
import operator
from security.Authentication import Authentication

class Message(dict):
    '''
        The Message Class extends a normal Dict.
        The Message is converted as JSON String and send through the Network.
    '''
    STATUS_NOT_AUTHENTICATED = "NOAUTH"
    STATUS_AUTHENTICATION_REJECTED = "AUTHREJECT"
    STATUS_ERROR = "ERROR"
    STATUS_OK = "OK"
    STATUS_LOGINOK = "LOGINOK"
    STATUS_CMD = "cmd"
      
      
    CMD_AUTHREQ = "AUTHREQ"  
    def __init__(self,cmd,body="",status="OK",error=False):
        '''
            @param cmd: command string
            @param body: message body
            @param status: Message.STATUS_X
            @param error: Boolean
        '''
        if status is not None and len(status)>0: 
            self["status"] = status
        
        if body is not None and len(body)>0:
            self['body'] =  body
        
        if error:
            self["error"] = error
        if cmd is not None and len(cmd)>0:            
            self['cmd'] = cmd
    
#m=Message("", "", Message.STATUS_AUTHENTICATION)
#m["user"]="admin"
#m["password"]="admin"
#print(json.dumps(m))

   
class ControlHandler(SimpleMessageIdentifyProtocol):
    '''
        The ControlHandler handles incoming TCP commands to control the security policies for the Proxy
        The Update Method also provides an interface for the Observer Pattern that extends the Class to an Observer. 
    '''
    
    def __init__(self):
        SimpleMessageIdentifyProtocol.__init__(self,False,0)
        self.authenticated=False
        self.wronglogins=0
        self._cmds = {"new":self._cmdNew,
                      "edit":self._cmdEdit,
                      "list":self._cmdList,
                      "delete":self._cmdDelete,
                      "general":self._cmdGeneral,
                      "genSrc":self._cmdGenSrc,
                      "genHost":self._cmdGenHost
                      }
        
        self._policyControl = PolicyControl().getInstance()
        self._policyControl.setChangeListener(self)
    
        
    def update(self):
        '''
            method for observer Pattern
        '''
        self._cmdList()
        
    def aMessage(self,msg):
        '''
            handles incoming messages and delegates to corresponding methods
        '''
        try:
            recv=json.loads(msg.decode())
        except Exception as e:
            Log.debug("invalid control command")
            self.protocolError()
            return

        try:
            if not self.authenticated:
                if self.inObj(["cmd","user","password"],recv) and  recv['cmd'] == Message.CMD_AUTHREQ:
                    if recv["user"] == StdConfig.getInstance().getCtrlUsername() and recv["password"] == StdConfig.getInstance().getCtrlPassword(): 
                        self.toClient(Message("", "", Message.STATUS_LOGINOK))
                        self.authenticated=True
                        Log.debug("logged in")
                        
                    else:
                        Log.debug("log in rejected");
                        self.toClient(Message("", "", Message.STATUS_AUTHENTICATION_REJECTED))
                        self.wronglogins+=1
                        if self.wronglogins >= 3:
                            self.doDisconnect()
                else:
                    self.toClient(Message("", "", Message.STATUS_NOT_AUTHENTICATED))
            else:
                #authenticated
                if self.inObj(["cmd","user","password"],recv) and recv['cmd'] == Message.CMD_AUTHREQ:
                    
                    #already autenticated
                    self.toClient(Message("", "", Message.STATUS_OK))
                    return
                
                if self.inObj(["cmd","status"], recv) and recv["status"] == "cmd":
                    if recv['cmd'] in self._cmds:
                        body=""
                        if "body" in recv:  
                            body=recv["body"]
                        self._cmds[recv['cmd']](body)
                        return
                    
                
                self.protocolError()

        except Exception as e:
            self.protocolError()
            raise e
            
     
    def protocolError(self):
        '''
            sends an error message to the client and disconnects.
        '''
        self.toClient(Message("","wrong protocol",Message.STATUS_ERROR,True))
        self.doDisconnect()
        
    def toClient(self,msg):
        '''
            @param msg: json-dumpable variable
            sends a msg as JSON string to the client.
        '''
        strs=json.dumps(msg)
        leng=str(len(strs))
        self.rawSend((leng+":"+strs).encode("UTF-8"))

    
    def _cmdNew(self,args,update=True):
        try:
            p=self.getPolicyFromDict(args)
            self._policyControl.addRule(p)
            if update:
                self._cmdList()
        except:
            self.toClient(Message("", "malformed data", Message.STATUS_ERROR, True))
            
            
        
        
    def _cmdEdit(self,args):
        try:
            self._cmdDelete(args["id"], False)
            self._cmdNew(args)
            self._cmdList()
        except:
            self.toClient(Message("", "malformed data", Message.STATUS_ERROR, True))
        
        
    def _cmdDelete(self,args,update=True):
        Log.debug("delete " + args)
        self._policyControl.removeRule(args)

        if update:
            self._cmdList()
        
    def _cmdList(self,args=None):
        #general
        p = self._policyControl.policies
        general = {}
        general["unknownPolicyRule"] = str(p.unknownPolicyRule)
        general["enabledSockets"] = str(p.enabledSockets)
        general["localSource"] = str(p.localSource)
        general["trustedSource"] = str(p.trustedSource)
        general["trustedDest"] = str(p.trustedDest)
        general["maxConnections"] = str(p.maxConnections)
        
        #specific
        
        #merge
        elems={}
        d={"specific":elems,"general":general}
        ret=Message("list", d, Message.STATUS_OK)
        for k,v in self._policyControl.policies.specificRules.items():
            elems[k]=self.getDictFromPolicy(v)
        
        self.toClient(ret)
    
    def _cmdGeneral(self,args):
        try:
            self._policyControl.updateGeneral(args)
            self._cmdList()
        except:
            self.protocolError()
        
        
    def _cmdGenHost(self,host):
        
        snd=Authentication.generateHostkey(host.encode("UTF-8"))
        self.toClient(Message("hostkey", snd[0].decode("UTF-8")+snd[1]))
        
    def _cmdGenSrc(self,n=None):
        snd=Authentication.generateSourcekey()
        self.toClient(Message("srckey", snd[0].decode("UTF-8")+snd[1]))
        
    
    def getPolicyFromDict(self,d):
        '''
            @return Policy() from a dict.
            The dict must contain all keys: ["action","dest","port","src","type"] 
        '''
        if not self.inObj(["action","dest","port","src","type"],d):
            return self.protocolError()
        
        
        type_=Types(Types.TCP.lower() in d["type"],Types.UDP.lower() in d["type"], Types.UNIX.lower() in d["type"])
        if type_.isUnix() and not type_.isTCP() and not type_.isUDP():
            ret = Policy(d["action"], d["dest"], 0, d["src"], type_)
        else:
            ret = Policy(d["action"], d["dest"], int(d["port"]), d["src"], str(type_))
        return ret
        
    
    def getDictFromPolicy(self,policy):
        '''
            returns a dict from a Policy()
        '''
        d = {}
        d["action"] = policy.action
        d["dest"] = policy.dest
        d["port"] = str(policy.port)
        d["src"] = policy.src
        d["type"] = policy.type
        return d
    

    
    def inObj(self,elems,obj):
        '''
         @return: True, if all elements in elems are in obj
         works with every "in" operator supported object
        '''
        return functools.reduce(operator.and_,map(lambda x: x in obj,elems),True)
    


class ControlInterface(Thread):
    '''
        Thread that creates a TCP SockServer with ControlHandler.
        The Server listens to one connection and disconnects the old one if a new is established.
    '''
    def __init__(self,port):
        Thread.__init__(self)
        self.setDaemon(True)
        self.port=port
    def run(self):
        try:
            self.__s=SockServer(SocketModeFactory.TCP, ControlHandler,1)
            #self.__s.taskManager.config(autokick=False)
            self.__s.setReuseAdress()
            self.__addr = ("localhost",self.port)
            self.__s.bind(self.__addr)
            Log.info("control interface started: %s"%(self.__addr,))
            
            self.__s.start()
        except socket.error:
            Log.error("control interface could not bound on %s",(self.__addr,))
            



