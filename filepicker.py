import Tkinter,tkFileDialog
import tkMessageBox
import sys
import pdb

def pickfile(path='.'): #add filetypes
    root = Tkinter.Tk()
    root.withdraw()
    f = tkFileDialog.askopenfilename(parent=root,title='Choose a file')
    if f:
        root.destroy()
        del root
        return f
    else:
        print "No file picked, exiting!"
        root.destroy()
        del root
        sys.exit()

def saveasfile(path='.', filetypes = [], defaultextension=''): #add filetypes
    root = Tkinter.Tk()
    root.withdraw()
    f = tkFileDialog.asksaveasfilename(parent=root,title='Choose a filepath to save as',filetypes = filetypes,defaultextension=defaultextension)
    if f:
        root.destroy()
        del root
        return f
    else:
        print "No file picked, exiting!"
        root.destroy()
        del root
        sys.exit()

        
def pickfiles(path='.', filetypes = [], defaultextension=''): 
    root = Tkinter.Tk()
    root.withdraw()
    f = tkFileDialog.askopenfilenames(parent=root,title='Choose a file',filetypes = filetypes)
    if f:
        f=root.tk.splitlist(f)
        root.destroy()
        del root
        return f
    else:
        print "No file picked, exiting!"
        root.destroy()
        del root
        sys.exit()
        

def pickdir(path='.'):
    root = Tkinter.Tk()
    root.withdraw()
    dirname = tkFileDialog.askdirectory(parent=root,initialdir=".",title='Please select a directory')

    root.destroy()
    if len(dirname ) > 0:
        return dirname
    else:
        print "No directory picked, exiting!"
        sys.exit()

def askyesno(title = 'Display?',text = "Use interactive plotting?"):
    root = Tkinter.Tk()
    root.withdraw()
    tf = tkMessageBox.askyesno(title, text)
    root.destroy()
    return tf




    
##
### ======== "Save as" dialog:
##import Tkinter,tkFileDialog
##
##myFormats = [
##    ('Windows Bitmap','*.bmp'),
##    ('Portable Network Graphics','*.png'),
##    ('JPEG / JFIF','*.jpg'),
##    ('CompuServer GIF','*.gif'),
##    ]
##
##root = Tkinter.Tk()
##fileName = tkFileDialog.asksaveasfilename(parent=root,filetypes=myFormats ,title="Save the image as...")
##if len(fileName ) > 0:
##    print "Now saving under %s" % nomFichier

if __name__=='__main__':
##    f = pickfile()
##    d = pickdir()
##    s=saveasfile(filetypes = [("Shelve files",'*.shv'), ('All','*') ],defaultextension='.shv')
    fs = pickfiles(filetypes=[('AVI videos','*.avi'),('All files','*.*')])
    print fs
    print type(fs)
