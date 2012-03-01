'''
Created on 22.11.2011

@author: phil
'''
import os
from  xml.etree import ElementTree as elemTreeModule
 
from config.Config import Log
from security.PolicyData import Policies, Types, Policy

from xml.etree.ElementTree import  Element, ElementTree

from xml.dom import minidom

class PolicyParser(object):
    '''
    This class reads and writes policy rules from/to xml files 
    '''
    #xmlcontent: string representation of the loaded xml file
    #filename: path to the xml file
    

    def __init__(self,filename):
        self.filename=filename
        if not os.path.exists(filename):
            Log.warning("Policy XML-File not found")
            #print("Policy XML-File not found")
            
            
            policies = Policies() # generating standard polices
            policies.addRule(Policy())
            xml=self.toXML(policies)
            
            self.write(xml)
        
        
        #try:
        #    self.load()
        #except:
            #Log.error("policy file has wrong format")
        #    print("policy file has wrong format")
    
    def load(self):
        '''
            loads the xml file as Policies()
        '''
        xml=elemTreeModule.parse(open(self.filename))
        tree=ElementTree(xml)
        return self.toObject(tree)
        

        
    def write(self,xml):
        '''
            writes down the xml
        '''
        with open(self.filename,"w") as f:
            f.write(self.prittyfy(xml))
        
        
        
    
    def prittyfy(self,xml):
        '''
            makes the xml humand readable
            @param xml: the xml that should be formatted
            @return a human readable xml string
        '''
        str = elemTreeModule.tostring(xml.getroot(), 'utf-8')
        prt = minidom.parseString(str)
        return prt.toprettyxml(indent="  ")
    
    def toXML(self,data):
        '''
        serializes the data to an xml file
        @param data: Policies() 
        '''
        
        tree = ElementTree(Element("policies"))
        tag=tree.getroot()
        g=Element("general")
        tag.append(g)
        
        g.append(Element("policy",{"rule":data.unknownPolicyRule}))
        g.append(Element("localSource",{"action":data.localSource}))
        g.append(Element("trustedDest",{"action":data.trustedDest}))
        g.append(Element("trustedSource",{"action":data.trustedSource}))
        
        for e in Types.all():
            g.append(Element(e.lower(),{"enabled": str(e in data.enabledSockets)}))
            
        maxc=Element("maxConnections")
        g.append(maxc)
        maxc.text=str(data.maxConnections)
        
        
        sp=Element("specific")
        
        
        for specificRules in data.specificRules.values():
            ol=dir(object)
            m=(d for d in dir(specificRules) if (not callable(d) and d not in ol and not d.startswith("_") and d not in ["ASK","ANY","ALLOW","DENY"]))

            attr={}
            for n in m:
                attr[n]=str(getattr(specificRules, n))

            
            sp.append(Element("policy",attr))
        
        tag.append(sp)
        
        return tree
        
    def toObject(self,xml):
        '''
            creates a Policies() out of a serialized policy xml file
            @return Policies()
        '''
        ret=Policies()
        elem = xml.getroot()
        
        
        
        gl=elem.find("general")
        ret.unknownPolicyRule=gl.find("policy").attrib["rule"]
        ret.enabledSockets.enableTCP(gl.find("tcp").attrib["enabled"].lower()=="true")
        
        ret.enabledSockets.enableUDP(gl.find("udp").attrib["enabled"].lower()=="true")
        ret.enabledSockets.enableUNIX(gl.find("unix").attrib["enabled"].lower()=="true")
        
        ret.maxConnections=int(gl.find("maxConnections").text.strip())
        ret.localSource=gl.find("localSource").attrib["action"]
        ret.trustedDest=gl.find("trustedDest").attrib["action"]
        ret.trustedSource=gl.find("trustedSource").attrib["action"]
        
        
        sc=elem.find("specific")
        for e in sc:
            policy = Policy()
            for k,v in e.attrib.items():
                if k == "port":
                    try:
                        v=int(v)
                    except:
                        v=0
                setattr(policy, k,v)
                
            ret.specificRules[str(policy)]=policy
            
        
        return ret
        
        
        
    
    def printXML(self,tree):
        print(self.prittyfy(tree))
            

if __name__ == "__main__":            
    p = PolicyParser("../../resources/p.xml")
    print(p.load())