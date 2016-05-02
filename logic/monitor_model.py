'''
monitor reads a configuration file named init.ini in order to determine what
operations from filelogic should be invoked on which directory.

@author: Andrew Manninen
@since: 16 November 2015
'''
import os
import traceback
from collections import Counter

class Rule:
    def __init__(self,op,ext,mod,pattern=None,newdir=None):
        self.op = op
        self.ext = ext            
        self.mod = mod
        self.pattern = pattern
        self.newdir = newdir
        
    def get(self):
        if self.op == None: return
        if self.ext == None: return
        if self.mod == None: return
        char = []
        char.append(self.op)
        char.append('|')
        char.append(self.ext)
        char.append('|')
        if isinstance(self.mod, list):
            char.append('[')
            char.append(self.mod[0])
            char.append(',')
            char.append(self.mod[1])
            char.append(']')
        else:
            char.append(self.mod)
        if self.op in ['delete','move']:
            char.append('|')
            char.append(self.pattern if not self.pattern == None else '')
            if self.op == 'move':
                char.append('|')
                char.append(self.newdir)
        return ''.join(char)

class Monitor:
    ''' Contain all the logic for reading the configuration file for applying
    rules to be used with filelogic.
    '''
        
    def __init__(self):
        ''' Launching point of the class.
        # mon is the type of monitor that will be used
        '''
        self.monitor = {}
            
    def add(self,direct,rule=None):
        ''' Add a new rule or directory to the monitor.
        '''
        
        if not direct in self.monitor:
            self.monitor.setdefault(direct,[])
            
        if not rule == None:
            if not rule in self.monitor[direct]:
                self.monitor[direct].append(rule)
                
    def remove(self,direct,rule=None):
        ''' Remove a rule or directory from the monitor.
        '''
        
        if not rule == None: 
            if rule in self.monitor[direct]:
                self.monitor[direct].remove(rule)
            
        elif direct in self.monitor:
            self.monitor.remove(direct)
    
    def removeAll(self):
        self.monitor = {}
    
    def read(self):
        ''' Read the init.ini. Because both rules and directories are stored
        in the init.ini file, they both must be read into the dictionary so
        that the monitor that is invoked can function properly.
        '''
        print('>>>Reading init.ini...')
        try:
            self.monitor = {}
            with open("init.ini") as file:
                lines = file.readlines()
                direct = ''
                for line in lines:
                    if "\t" in line:
                        self.monitor[direct].append(line.strip())
                    else:
                        direct = line.replace('\n','')
                        self.monitor.setdefault(direct,[])                
        except Exception as e:
            print (traceback.format_exc())
    
    def write(self):
        ''' Write what is currently in the daemon dictionary to file.
        '''
        print(">>>Writing init.ini...")
        try:
            try: os.remove("init.ini")
            except: pass
            with open("init.ini","w") as file:
                for direct in self.monitor:
                    file.writelines(direct + '\n')
                    for rule in self.monitor[direct]:
                        file.writelines('\t' + rule + '\n')
        except: print("Hello, nurse")
            
    def getList(self):
        return self.daemon[self.monitor]
            

    
if __name__ == '__main__':
    mon = Monitor()
    podcast = r"F:\Users\Andrew\Documents\Podcasts" + "\\" 
    mon.read()
    rule = Rule('delete','mp3','od7')
    mon.add(podcast,rule.get())
    print(mon.monitor)
    rule = Rule('copy','mp3','all')
    mon.add(r"F:\Users\Andrew\Documents\Podcasts" + "\\",rule.get())
    print(mon.monitor)
    
    mon.remove(r"F:\Users\Andrew\Documents\Podcasts" + "\\","delete|all|png")
    print(mon.monitor)

    mon.write()