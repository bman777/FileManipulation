'''
filelogic provides the functions for monitor to use in order to 
copy/move/delete/rename files in a directory.

@author: Andrew Manninen
@since: 16 November 2015
'''

import os, shutil # Import os for renaming and moving files/ shutil for copy
from datetime import datetime,date,timedelta # assists in converting epoch to a string
from os import listdir # used for listing the contents of a directory
from os.path import isfile, join
''' isfile returns if an item is a file 
# join combines a filepath and file
'''
from collections import Counter

class FileLogic:
    ''' Houses the logic to manipulate files in a directory
    '''
             
    def __init__(self, filepath):
        ''' Launching point of the class
        # This function is similar to a constructor
        '''
        self.filepath = filepath # Keep a class-level variable for the dir
        self.filedates = {}
        ''' Dictionary that is used to keep all the files sorted by their
        last modified date.
        '''
    
    def parseRawInput(self,rule):
        ''' Used in GUI_Launcher, this function parses a raw rule from Monitor
        and invokes the operation.
        '''
        counter = Counter(rule)
        rdir= None
        op = None
        ext = None
        mod = None
        pattern= None
        newdir = None 
        if counter["|"] is 3:
            rdir,op,ext,mod= rule.split("|")
        elif counter["|"] is 4:
            rdir,op,ext,mod,pattern= rule.split("|")
        elif counter["|"] is 5:
            rdir,op,ext,mod,pattern,newdir = rule.split("|")
            
        if "[" in mod:
            mod = mod.replace("[","").replace("]","")
            temp1, temp2 = mod.split(",")
            mod = []
            mod.append(temp1)
            mod.append(temp2)
        print(rdir,op,ext,mod,pattern,newdir)
        print(self.filepath)
        if rdir == self.filepath:
            if op == "copy":
                self.copy(mod, ext)
            elif op == "move":
                self.move(mod, ext, newdir, pattern)
            elif op == "delete":
                self.delete(mod, ext, pattern)
            elif op == "rename":
                self.rename(mod, ext)
    
    def readDirectory(self):
        ''' Read the contents of a directory and check if each item is a file.
        # If files are found, their modification date is determined and then
        added to the dictionary filedates for future access.
        '''
        self.filedates = {}
        for file in listdir(self.filepath):
            if isfile(join(self.filepath,file)):
                ''' If file is indeed a file add it to filedates
                '''
                fullname = self.filepath + file
                filedate = datetime.fromtimestamp(os.path.getmtime(fullname))\
                       .strftime("%Y.%m.%d") 
                ''' Convert the epoch time returned by os.path.getmtime into a
                string format of year.month.day.
                '''
                if not filedate in self.filedates:
                    ''' If filedates does not have the file's date stored as
                    a key yet, create a new key with the file's date
                    ''' 
                    self.filedates.setdefault(filedate,[])
                self.filedates[filedate].append(file)
                
    
    def parseFileExt(self, unparsed):
        ''' Split a file name from its extension and return both values.
        '''
        oldname, fileext = os.path.splitext(unparsed)
        return oldname, fileext
                    
    
    def displayStatus(self,op,ext,mod,pattern = None, newdir = None):
        ''' Display in the console what function is currently being invoked.
        '''
        if ext is "all" : ext = ""
        if isinstance(mod, list):
            temp1, temp2 = mod[0], mod[1]
            mod = "from {} to {}".format(temp1,temp2)
        elif 'n' in mod or 'o' in mod:
            if 'd' in mod:
                mod = '{} than {} day{}'.format('newer' if 'n' in mod else 'older', mod[2:], 's' if int(mod[2:])>0 else '')
        else:
            mod = "all time"
        if not pattern is None:
            if not newdir is None:
                print(">>>{} all {} files from {} containing \"{}\" to {}..."\
                      .format(op,ext,mod,pattern,newdir))
            else:
                print(">>>{} all {} files from {} containing \"{}\"..."\
                      .format(op,ext,mod,pattern))
        else:
            if not newdir is None:
                print(">>>{} all {} files from {} to {}..."\
                      .format(op,ext,mod,newdir))
            else:
                print(">>>{} all {} files {}...".format(op,ext,mod))
                
    
    def prepList(self,mod):
        ''' Create a temp dictionary for use in other functions.
        # mod is a modifier that can be either a range of dates that is
        fed in by a list or it can be the string "all" which represents all 
        dates in the directory.
        
        # Returns a copy of this newly prepared dictionary
        '''        
        def dateRange(d,mod,files,no=None):
            ''' If mod was a list, check if the date is within its range
            '''
            if not no == None:
                if 'd' in mod:
                    cd = date.today() - timedelta(days=int(mod[1:]))
                else:
                    cdate = mod.split('.')
                    cd = date(int(cdate[0]),int(cdate[1]),int(cdate[2]))
                mdate = d.split('.')
                md = date(int(mdate[0]),int(mdate[1]),int(mdate[2]))
                if no == 'n':
                    if md > cd: preplist[d] = files
                elif no == 'o':
                    if md < cd: preplist[d] = files
            else:
                if d >= mod[0] and date <= mod[1]:
                    preplist[d] = files
        
        preplist = {}
        for d,files in self.filedates.items():
            if 'n' in mod or 'o' in mod:
                dateRange(d, mod[1:], files, mod[0])
            if isinstance(mod, list): 
                dateRange(d, mod, files)
            else: 
                preplist[d] = files
        return preplist
                        
                
    def copy(self,mod,ext):
        ''' Copy files within a mod and with a specific file extension.
        Names the new files like the original with "-copy" added to the file
        name.
        '''
        
        def copyfile(filepath, file):
            filename, fileext = self.parseFileExt(file)
            shutil.copyfile(filepath+file,filepath+filename+"-copy"+fileext)

        copylist = self.prepList(mod)
        self.displayStatus("Copying", ext, mod)
        for d, files in copylist.items():
            for file in files:
                if not ext is "all":
                    ''' If the rule is not copying all file extensions
                    '''
                    fileext = self.parseFileExt(file)[1]
                    ''' Parse the file to extract its file extension. The ext
                    is the only thing needed for future computation so only
                    capture parseFileExt's fileext by only taking the second
                    value.
                    '''
                    if fileext.lower() == ext.lower():
                        copyfile(self.filepath,file)
                else:
                    copyfile(self.filepath,file)
                    
 
    def move(self,mod,ext,newdir,pattern = None):
        ''' Move files within a date range and with a specific file extension.
        A new directory must be specified for moving the files. Optionally a 
        pattern may be applied to move files based on if the pattern is found
        in the file name.
        '''
        
        def movefile(file):
            if "." in ext:
                ''' If there was an extension was specified by the function,
                parse the current file and check if the extensions match.
                '''
                fileext = self.parseFileExt(file)[1]
                if not fileext.lower() == ext.lower(): return
                ''' If the current file extension does not match the extension
                that is to be moved, return out of this function and continue
                looping through the main loop.
                '''
            if not os.path.exists(newdir): os.makedirs(newdir)
            ''' If the new directory specified by the main move function does
            not exist, create a new directory based on newdir
            '''
            cdir = self.filepath + file # current file and directory
            ndir = newdir + file # new file and directory
            try:
                os.rename(cdir, ndir)
                ''' To move files in Python, os.rename can be used because
                os.rename completely changes what the file name is (this 
                includes what the original path may have been). For this
                reason it is necessary to include the fullpath of the file in
                both the original file name and the new location.
                '''
            except:
                print("Cannot move {}".format(file))
        
        movelist = self.prepList(mod)
        self.displayStatus("Moving", ext, mod, pattern, newdir)
        for date, files in movelist.items():
            for file in files:
                if not pattern is None:
                    ''' If a pattern has been initiated by the invocation of
                    this method, check if the files match it
                    '''
                    if pattern in file:
                        movefile(file)
                else:
                    movefile(file)
        
            
    def delete(self,mod,ext,pattern = None):
        ''' Delete files within a date range and with a specific file 
        extension. Optionally a pattern may be applied to delete files based 
        on if the pattern is found in the file extension.
        '''
        
        def deletefile(file):
            if "." in ext:
                ''' If there was an extension specified by the function, parse
                the current file and check if the extensions match.
                '''
                fileext = self.parseFileExt(file)[1]
                if not fileext.lower() == ext.lower(): return
                ''' If the current file extension does not match the extension
                that is to be moved, return out of this function and continue
                looping through the main loop.
                '''
            fullname = self.filepath + file
            os.remove(fullname)
        
        deletelist = self.prepList(mod)
        self.displayStatus("Deleting", ext, mod, pattern)
        for date, files in deletelist.items():
            for file in files:
                if not pattern is None:
                    ''' If a pattern has been initiated by the invocation of
                    this method, check if the files match it
                    '''
                    if pattern in file:
                        deletefile(file)
                else:
                    deletefile(file)
            
    def rename(self,mod,ext,pattern = None):
        ''' Rename files within a date range and with a specific file 
        extension. Optionally a pattern may be applied to rename files based
        on if the pattern is found in the file extension. The renamed files 
        take their modified date and use it as base for the new file name.
        '''
        
        def renamefile(file,cnt):
            fileext = self.parseFileExt(file)[1] 
            if "." in ext and not fileext.lower() == ext.lower(): return
            ''' If there was an extension specified by the function and the
            file extensions do not match, return to the loop. 
            '''
            fullname = self.filepath + file
            newname = datetime.fromtimestamp(os.path.getmtime(fullname))\
                            .strftime("%Y-%b-%d")+"-{:0>3d}".format(cnt)+fileext
            os.rename(fullname, fullname.replace(file,newname))  
            
        renamelist = self.prepList(mod)
        self.displayStatus("Renaming", ext, mod, pattern)
        for date, files in renamelist.items():
            cnt = 0
            for file in files:
                if not pattern is None:
                    ''' If a pattern has been initiated by the invocation of
                    this method, check if the files match it
                    '''
                    if pattern in file:
                        renamefile(file,cnt)
                else:
                    renamefile(file,cnt)       
                cnt += 1
            
def main():
    filepath = r"F:\Users\Andrew\Downloads" + "\\"
    f = FileLogic(filepath)
    f.readDirectory()
    f.copy("nd7",".png")
   # f.rename(["2015.10.30", "2015.11.01"],"all")
    f.readDirectory()
    f.delete("all","all","-copy")
   # f.move("all","all",filepath+"copies\\","-copy")
    
    
if __name__ == '__main__': main()