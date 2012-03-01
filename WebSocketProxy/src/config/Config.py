'''
Created on 20.11.2011

@author: phil
'''


from configparser import SafeConfigParser, NoOptionError
from datetime import date as ddate
import time
import os
import sys

class Config(object):
    '''
    A generic Configfile that uses singleton pattern and SafeConfigParser
    '''
    _instance=None


    def __init__(self,filename,defaults):
        '''
        @param filename: the path/name of the configfile
        @param defualts: default settings: {'section'{'key':'value'}} 
        '''
        
        self._filename=filename
        self._defaults=defaults
        
        if not os.path.exists(filename):
            fp=open(self._filename,"wb")
            fp.close();
            Log._log(Log.WARNING,"Configfile does not exist")
        
        self._cfp = SafeConfigParser()
        
        self.load()   
        self._expandParser()              
        self.save()
   
    
    def _expandParser(self):
        
        for kD,vD in self._defaults.items():
            if not self._cfp.has_section(kD):
                self._cfp.add_section(kD)
            for kS,vS in vD.items():
                try:
                    self._cfp.get(kD, kS)
                except NoOptionError:
                    self._cfp.set(kD, kS, vS)
          
    
    def __str__(self):
        '''
        @return: the section and values of the configfile
        '''
        ret=""
        for kD,vD in self._cfp.items():
            ret="".join([ret,"Section:",str(kD),"\n"])
            for kS,vS in vD.items():
                ret="".join([ret," ",str(kS),": ",str(vS),"\n"])
                
        return ret
    
    def load(self):
        '''
        reads the file and stores the values
        '''
        self._cfp.readfp(open (self._filename,"r"))
        self._cfp.read(self._filename)
        
    def save(self):
        '''
        writes down the file 
        '''
        with open(self._filename,"w") as f:
            self._cfp.write(f)
        
                

             
            

    @staticmethod
    def getInstance():
        '''
        singleton instance
        '''
        
        if Config._instance == None:
            Config._instance = Config()
           
        return Config._instance
    





class StdConfig(Config):
    '''
    the standard config file
    '''
    def __init__(self):
        Config.__init__(self,"../resources/default.cfg",{"logging":
                                                         {"verboselevel":"5",
                                                          "log_warnings":"true",
                                                          "log_infos":"false",
                                                          "log_errors":"true",
                                                          "log_policy":"false",
                                                          "log_debug":"false"},
                                                         "proxy":
                                                         {"port":"8080"},
                                                         "control":
                                                         {"port":"8081",
                                                          "user":"admin",
                                                          "password":"admin",
                                                          "enabled" : "true"}
                                                         })
            

    def getVerboseLevel(self):
        '''
        @return: the current verbose level
        '''
        return int(self._cfp.get("logging","verboselevel")) 
    
    def logInfos(self):
        '''
        @return: True if the logfile for infos is on  
        '''
        return (self._cfp.get("logging","log_infos")=="true")
    
    def logWarnings(self):
        '''
        @return: True if the logfile for warning is on  
        '''
        return (self._cfp.get("logging","log_warnings")=="true")
    
    def logErrors(self):
        '''
        @return: True if the logfile for errors is on  
        '''
        return (self._cfp.get("logging","log_errors")=="true")
    
    def logPolicy(self):
        '''
        @return: True if the logfile for policy control is on  
        '''
        return (self._cfp.get("logging","log_policy")=="true")

    def logDebug(self):
        '''
        @return: True if the logfile for debug is on  
        '''
        return (self._cfp.get("logging","log_debug")=="true")    
    
    
    def getProxyPort(self):
        '''
        @return: the port where the websocket proxy listens on
        '''
        return int(self._cfp.get("proxy","port"))
  
    def getControlPort(self):
        '''
          @return: the port where the control socket is listening
        '''
        return int(self._cfp.get("control","port"))
  
    def isControlInterfaceEnabled(self):
        '''
          @return: True if the interface is enabled
        '''
        return self._cfp.get("control","enabled") == "true"
    
    def getCtrlUsername(self):
        '''
          @return: The username for the controlinterface
        '''
        return self._cfp.get("control","user")
    
    def getCtrlPassword(self):
        '''
          @return: The password for the controlinterface
        '''
        return self._cfp.get("control","password")
    
    @staticmethod
    def getInstance():
        
        if Config._instance == None:
            Config._instance = StdConfig()
           
        return Config._instance
################## LOG ###################    
    



class LogType(object):
    '''
    Every Log Event has a Type with a log level (verbose level) and a name e.g. ERROR
    LogTypes are specified in @see: Log
    '''
    MAX = 4
    def __init__(self,level,name):
        self.level=level
        self.name=name
        
    
        
class Log(object):
    '''
    a static log object
    '''
    ERROR=LogType(1,"ERROR") # an error normally shuts down the program
    WARNING=LogType(2,"WARNING")# warnings are outputted, if something exceptional occured, but the program handles it
    INFO=LogType(3,"INFO")# infos are things like 'program starts..'
    POLICYCONTROL=LogType(4,"POLICYCONTROL") # if a script is blocked by a policy
    DEBUG=LogType(5,"DEBUG")# debugmessages
    
    
    
    @staticmethod
    def _log(type,msg,channel=sys.stdout):
        '''
        call for all events that shoud be logged and for verbose out
        @param type: LogType
        @param msg: a log message 
        '''
        Log._verbose(type, msg,channel)
        Log._logMultiplexer(type, msg)
    
    @staticmethod    
    def error(msg,exit=True):
        Log._log(Log.ERROR,msg,sys.stderr)
        if exit:
            sys.exit(1)

    @staticmethod    
    def warning(msg):
        Log._log(Log.WARNING,msg)

    @staticmethod    
    def info(msg):
        Log._log(Log.INFO,msg)

    @staticmethod    
    def policycontrol(msg):
        Log._log(Log.POLICYCONTROL,msg)

    @staticmethod    
    def debug(msg):
        Log._log(Log.DEBUG,msg)

                
    @staticmethod        
    def _logMultiplexer(type,msg):
        if type  == Log.WARNING and not StdConfig.getInstance().logWarnings():
            return
        
        if type  == Log.ERROR and not StdConfig.getInstance().logErrors():
            return
        if type  == Log.DEBUG and not StdConfig.getInstance().logDebug():
            return
        if type  == Log.INFO and not StdConfig.getInstance().logInfos():
            return
        if type  == Log.POLICYCONTROL and not StdConfig.getInstance().logPolicy():
            return
        
        date=ddate.fromtimestamp(time.time())

        d="".join(["../resources/logs/",str(date.month),"_",str(date.year)])
        if not os.path.exists(d):
            os.mkdir(d)
        
        t=time.strftime("%d.%m.%Y %H:%M:%S")
        f="".join([d,"/",type.name,".log"])
        with open(f,"a") as fp:
            m="".join([t,": ",type.name,"\t",msg,"\n"])
            fp.write(m)
        
            
        
    
    @staticmethod
    def _verbose(type,msg,channel):
        
        vlevel=StdConfig.getInstance().getVerboseLevel()
        
        if vlevel >= type.level:
            print(type.name+":",msg,file=channel)