'''
Created on Dec 27, 2011

@author: phil
'''

from tkinter import *
from tkinter.simpledialog import Dialog
from security.PolicyData import Policy,  Types








class AskPrompt(object):
    '''
        Class that holds static Methods to show the Firewall Dialog
    '''

    @staticmethod
    def showAskDialog(pol,policy,auth="n/a"):
        root = Tk()
        root.withdraw()
        
        type=pol.type
        
        src=pol.src
        dest=pol.dest
        if type != Types.UNIX:
            dest=pol.dest+":"+str(pol.port)
        
        auth=auth
        
        ret=Prompt(root,"socket.js - guard",type,src,dest,auth)
        
        if ret.action == 0:
            root.destroy()
            return False
        
        action, rem = ret.dec_,ret.rem_
        
        if rem:
            if action == 0:
                pol.action="allow"
            else:
                pol.action="deny"
            
            
            policy.addRule(pol)
        root.destroy()   
        return action == 0
    






class Prompt(Dialog):
    '''
        Firewall Dialog that asks if a script has permission to establish a connection
    '''
    
    def __init__(self, parent,title,type,src,dest,auth):
        self.type=type
        self.src=src
        self.dest=dest
        self.auth=auth
        self.action=0
        self.rem_ = None
        self.dec_ = None
        Dialog.__init__(self, parent, title)
        
        
    def body(self, master):
        row=0
        
        labelopts = {"sticky":W}
        Label(master, text="A script is asking for accesss:").grid(row = row, column = 0,columnspan=2)
        row+=1
        Label(master, text="Type: %s"%self.type).grid(row=row, column = 0,**labelopts)
        row+=1
        Label(master, text="Source: %s"%self.src).grid(row=row, column = 0,**labelopts)
        row+=1
        Label(master, text="Destination: %s"%self.dest).grid(row=row, column = 0,**labelopts)
        row+=1
        Label(master, text="Authentications: %s"%self.auth).grid(row=row, column = 0,**labelopts)
        row+=1
        
        self.decide = IntVar(0)
        self.remember = IntVar(0)
        allow = Radiobutton(master,text="allow",variable = self.decide,value = 0)
        deny = Radiobutton(master,text="deny",variable = self.decide, value = 1)
        
        
        allow.grid(row = row, column = 0)
        deny.grid(row = row, column = 1)
        
        row+=1
        remember=Checkbutton(master,text="remember",variable=self.remember)
        remember.grid(row = row, column = 0,columnspan = 2,sticky = W)
        
        allow.select()
        

    def apply(self):
        
        self.action=1
        self.dec_ = self.decide.get()
        self.rem_ = self.remember.get()
        
    def cancel(self,event=None):
        Dialog.cancel(self, event)
#p=Policy()

#AskPrompt.showAskDialog(p)


