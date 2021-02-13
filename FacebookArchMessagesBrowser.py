# Facebooki arhiivi lehitseja
# ukj@ukj.ee, 2021

import os
import tkinter as tk
#from tkinter import font
from tkinter import filedialog, messagebox
#from tkinter.filedialog import asksaveasfile
from tkinter.ttk import *
import thirdparty.CreateToolTip

from ukj_ee.FbMessagesArchive import *
from  ukj_ee.yt_basicMeta import yt_basicMeta

'''
import webbrowser
#from parsers.config import config
#from parsers.utils import export_dataframe, detect_language
#import logging
#from collections import defaultdict
#import glob
#import locale
#import codecs
#locale.getpreferredencoding()
'''




class AppHelpWindow(tk.Toplevel):
    '''Abiaken
    
    * https://www.geeksforgeeks.org/open-a-new-window-with-a-button-in-python-tkinter/
    * https://www.askpython.com/python/examples/find-all-methods-of-class
    
Ava zip\t\tCtrl-O
Salv csv\t\tCtrl-S
Kopeeri kõik\tCtrl-Alt-C
See abi\t\tF1
Välju\t\tCtrl-Q

    '''      
    def __init__(self, parent): 
        super().__init__(parent)
        text_title="Facebook Sõnumite JSON arhiiv zip"
        text = f"""
\t{text_title}
\t--- --- ---

* Loeb zip faili ilma kõike lahti pakkimata
* Filtreeritud teksti saab kopeerida lõikelauale või salvestada CSV
* Näitab manuste failiteesid ja tekstis leiduvaid linke
* Lisab Youtube JSON API-t kasutades video linkidele pealkirjad ja salvestab need SQLite abil.


\tukj@ukj.ee, 2021.02"""
        
        self.title(text_title)
        label = Label( self, text=text, relief=tk.RAISED, wraplength=600)
        label.pack()   
        self.update()
        h=int(self.winfo_height())
        w=int(self.winfo_width())
        self.geometry(f"{w}x{h}")

        





class App(tk.Tk):
    ''' Rakenduse peaaken'''
    yt=None
    yt_cache = ''
    yt_API_key = ''
    own_name='Nimi'
    fbmsg = FbMessagesArchive()
    msg_boxes = []
    msg_convs = []
    result = []
    current_box = current_thread = ''
    #root=None
    T=None
    listbox_Box=None
    listbox_Thread=None
    appButtons = {}
    csw = 700
    csh = 700
    frame=None
    
    def __init__(self):
        '''Peaaknaga alustamine
        
        * https://www.plus2net.com/python/tkinter-listbox.php
        * https://www.geeksforgeeks.org/scrollable-listbox-in-python-tkinter/
        * https://tk-tutorial.readthedocs.io/en/latest/listbox/listbox.html  
        
        '''
        super().__init__()
        
        self.scw = self.sch = 700
        self.frame = Frame(self, height = self.scw, width = self.sch)
        self.frame.pack()
                
        self.title("Facebooki Sõnumite Arhiiv")
        self.resizable(True, True) #Mis suunal suurus muudetav X Y
        self.update()
        
        
        S = tk.Scrollbar(self.frame)
        self.T = tk.Text(self.frame, height=50, width=80)
        #courier14 = tkFont.Font(family="Courier",size=14,weight="bold")
        #self.T.insert(tk.END, font.nametofont("TkFixedFont").actual())
        #self.T.insert(tk.END, "\n".join(result))
        
        S .config(command=self.T.yview)
        self.T.config(yscrollcommand=S.set, state=tk.NORMAL)
        
        group_1 = tk.LabelFrame(self.frame, padx=15, pady=10, text="Toimingud")
                
        self.listbox_Box = tk.Listbox(group_1,height=3, selectmode='browse', selectbackground='blue',highlightcolor='yellow',highlightthickness=1) 
        listboxScroll_Box = Scrollbar(group_1)
        self.listbox_Box.config(yscrollcommand = listboxScroll_Box.set) 
        listboxScroll_Box.config(command = self.listbox_Box.yview)
        self.listbox_Box.bind('<<ListboxSelect>>', self.listboxSel_Box)
        
        self.listbox_Thread = tk.Listbox(group_1,height=3, selectmode='browse',selectbackground='blue',highlightcolor='yellow',highlightthickness=1)
        listboxScroll_Thread = Scrollbar(group_1)
        self.listbox_Thread.config(yscrollcommand = listboxScroll_Thread.set)
        listboxScroll_Thread.config(command = self.listbox_Thread.yview)
        self.listbox_Thread.bind('<<ListboxSelect>>', self.listboxSel_Thread)
       
        #
        #Nuppude loomine ja töövahendite järjestamine
        #
        self.create_AppButton(group_1, 'fileOpen', 'Ava',self.key_openfile, text_tooltip='Ava arhiiv zip', controlkey='<Control-o>')
        self.create_AppButton(group_1, 'fileSave', 'Salv\nCSV',self.key_savefile, text_tooltip='Salvesta filtreering tekstina', controlkey='<Control-s>')       
        self.create_AppButton(group_1, 'copyAll', 'Kopeeri',self.textbox_copy, text_tooltip='Kopeeri kogu see vestlus', controlkey='<Control-Alt-c>')
        #self.create_AppButton(group_1, 'clear', 'Tühj.',self.key_savefile, text_tooltip='Tühjenda', controlkey='<Control-e>')        
        self.listbox_Box.pack(side=tk.LEFT)
        listboxScroll_Box.pack(side = tk.LEFT, fill = tk.BOTH)
        self.listbox_Thread.pack(side=tk.LEFT)
        listboxScroll_Thread.pack(side = tk.LEFT, fill = tk.BOTH)
        self.create_AppButton(group_1,'helpWin','[ ? ]',self.key_helpWindow, text_tooltip='Salvesta filtreering tekstina', controlkey='<F1>')
        self.create_AppButton(group_1,'exitApp','[ X ]', self.key_exit, text_tooltip='Lõpeta', controlkey='<Control-Q>')
        group_1.pack()

        self.T.pack(expand=tk.YES, side=tk.LEFT, fill=tk.BOTH)
        S.pack(side=tk.RIGHT, fill=tk.Y)
        self.update()
        
        
        self.scw = self.winfo_width()
        self.sch = self.winfo_height()
        self.frame.config(width=self.scw, height=self.sch)
        self.geometry(f"{self.scw}x{self.sch}")
        self.update()
        #self.mainloop()
        #myLogger('App.__init__()', " end") 



    def set_yt_api_key(self, key):
        '''       
        Returns
        -------
        bool
        '''
        
        if isinstance(key, str):
            self.yt_API_key=key
            return True
        else:
            return  False

    def create_AppButton(self, group, name, text,cmd,  text_tooltip='', controlkey=''):
        '''Nuppude tegija
        
        * https://www.daniweb.com/programming/software-development/threads/111526/setting-a-string-as-a-variable-name
        * https://stackoverflow.com/questions/50615371/accessing-tkinter-buttons-found-in-a-dictionary
        * https://stackoverflow.com/questions/16082243/how-to-bind-ctrl-in-python-tkinter
        * #exec("%s = %d" % (name, 2))
        * food = 'bread'; vars()[food] = 123; print bread  # --> 123
        * vars(self)['a'] = 10; print(self.a)
        '''
        b = tk.Button(group, text=text, command=cmd, width=5)
        b.config(width=5, height=2)
        
        if text_tooltip != '':
            if controlkey != '':
                text_tooltip +=  ' ' + controlkey.title() 
            thirdparty.CreateToolTip.CreateToolTip(self, b, text_tooltip)
        
        if controlkey != '':
            self.frame.bind(controlkey, cmd)
            #print(f"abc {controlkey} {cmd}")
        b.pack(side=tk.LEFT)
        self.appButtons[name] = b
        self.update()




    def update_AppButton(self, name, text):
        '''Nupu kirja muutmine'''
        self.appButtons[name].configure(text=text)



    def dict_keys(self, d):
        ''' Get dict{} keys, returns list[] '''
        k = []
        for i in d: 
            k.append(i)
        return k
    
    def textbox_clear(self):
        self.T.tag_add('sel', '1.0', 'end')
        self.T.delete(1.0, 'end')
        self.update()
        self.T.tag_remove('sel', '1.0', 'end')
        
    
            
    def textselect(self, parent,textwidget):
        parent.event_generate("<<TextModified>>")
        textwidget.focus()
        textwidget.tag_add('sel', '1.0', 'end')
    
    
    def textbox_copy(self):
        '''
        * https://mail.python.org/pipermail/tutor/2004-July/030398.html
        * https://stackoverflow.com/questions/64251762/python-tkinter-select-and-copy-all-text-contents-to-clipboard-on-button-clic
        * https://stackoverflow.com/questions/20611523/tkinter-text-widget-unselect-text
        '''
        self.root.clipboard_clear()
        self.T.focus()
        self.T.event_generate("<<TextModified>>")
        self.T.tag_add('sel', '1.0', 'end')   
        self.clipboard_append( self.T.get("sel.first", "sel.last") )
        self.update()
        self.T.tag_remove('sel', '1.0', 'end')
    

    def listboxSel_Box(self, event):
        #global T, listbox_Box, fbmsg, msg_convs, own_name, yt, current_box, current_thread
        anchor=str( self.listbox_Box.get(tk.ANCHOR) )
        selection=event.widget.curselection()
        if selection:
            index = selection[0]
            value = event.widget.get(index)
        elif anchor:
            value=anchor 
        else:
            value='inbox'
    
        if self.fbmsg.is_loaded() is False:
            return False
        
        self.listbox_Thread.delete(0, 'end') 
        self.fbmsg.get_threadBoxes() #msg_boxes =
        self.msg_convs = self.fbmsg.get_conversations(value)
        persons =   self.dict_keys(self.msg_convs)
        value=''
        if len(persons) > 0:
            p1 = persons[0]
            first_thread = self.msg_convs[p1]
            for element in self.msg_convs:
                self.listbox_Thread.insert(tk.END,element)
               
            self.listbox_Thread.selection_set( first = 0 )
            self.listbox_Thread.select_set(0) #This only sets focus on the first item.
            self.listbox_Thread.event_generate("<<ListboxSelect>>")
        
            self.fbmsg.load_conversation(first_thread , self.own_name)
            self.result = self.fbmsg.get_conversation_filtered('attachments ytmeta', self.yt)
            self.current_box = value
            self.current_thread = p1
            
            self.textbox_clear()
            #myLogger('box()', f"box 1 thr {first_thread}\n\n {p1}\n{persons} \n\n{self.msg_convs}")
            self.T.insert(tk.END, f"\n f thr {first_thread}\n")
            self.T.insert(tk.END, f"\n box {value}\n\n{first_thread}\n{self.msg_convs}")
            self.T.insert(tk.END, "\n".join(self.result))
        
    
    def listboxSel_Thread(self, event):
        anchor=str(self.listbox_Thread.get(tk.ANCHOR))
        selection=event.widget.curselection()
        value=''
        if selection:
            index = selection[0]
            value = event.widget.get(index)
        elif anchor:
            value=anchor    
        
        if value != '':
            #persons = dict_keys(msg_convs)
            thread = self.msg_convs[value]
            self.msg_boxes = self.fbmsg.get_threadBoxes()
            
            self.fbmsg.load_conversation(thread, self.own_name)
            self.result = self.fbmsg.get_conversation_filtered('attachments ytmeta', self.yt)
            self.current_box = 'inbox'
            self.current_thread = value
                
            #myLogger('thread()', "tyhj")
            self.textbox_clear()
            self.T.insert(tk.END, f"\n thread {value} {thread}\n\n\n")
            self.T.insert(tk.END, "\n".join(self.result))
            #myLogger('thread()', "res")
    
        
    def key_helpWindow(self):
        window = AppHelpWindow(self)
        window.grab_set()
        
        
                    
    def key_openfile(self):
        '''
        * https://www.geeksforgeeks.org/python-askopenfile-function-in-tkinter/
        * https://runestone.academy/runestone/books/published/thinkcspy/GUIandEventDrivenProgramming/02_standard_dialog_boxes.html
        '''
        #myLogger('open()', f" start") 
        files = [('Zip Files', '*.zip')]
        file = filedialog.askopenfilename(filetypes = files, defaultextension = files)
        try:
            isf = os.path.isfile(file)
        except:
            isf = False
            
        if isf:
            if self.fbmsg.set_ZipFp(file):
                # skripti  kataloogis
                #yt_cache_path = os.path.splitext(os.path.basename(file))[0]+'.yt.sqlite'
                # Fb arhiivi kõrval
                yt_cache_path = os.path.splitext(file)[0]+'.yt.sqlite'
                messagebox.showinfo("Teave",f"""Youtubest teabe hankimine võib kaua aega võtta.
Fb zip asukoht: {file}
Fb sqlite asukoht: {yt_cache_path}
""")
                self.yt = yt_basicMeta(key=self.yt_API_key, cache=yt_cache_path)
                self.listbox_Box.delete(0,tk.END)
                self.listbox_Thread.delete(0,tk.END)
                           
                self.msg_boxes = self.fbmsg.get_threadBoxes()
                self.msg_convs = self.fbmsg.get_conversations('inbox')
                
                persons = self.dict_keys(self.msg_convs)
                p1 = persons[0]
                thread = self.msg_convs[p1]
                for element in self.msg_boxes:
                    self.listbox_Box.insert(tk.END,element)
                #myLogger('open()', f"convs {p1}\n{persons}\n\n")    
                self.listbox_Box.selection_set( first = 0 )
                self.listbox_Box.select_set(0) #vali esimene
                self.listbox_Box.event_generate("<<ListboxSelect>>")
                
                for element in self.msg_convs:
                    self.listbox_Thread.insert(tk.END,element)
                self.listbox_Thread.selection_set( first = 0 )
                self.listbox_Thread.select_set(0) # vali esimene
                self.listbox_Thread.event_generate("<<ListboxSelect>>")
                #myLogger('open()', f"convs {self.msg_convs}")
                        
                self.fbmsg.load_conversation(thread , self.own_name)
                self.result = self.fbmsg.get_conversation_filtered('attachments ytmeta', self.yt)
                self.current_box = 'inbox'
                self.current_thread = p1
                
                self.textbox_clear()
                self.T.insert(tk.END, "\n".join(self.result))
            else:
                self.result = []
                
        
    
    def key_savefile(self):
        ''' Kirjutab tekstikasti sisu faili, mille nimeks soovitab Avatus kirjakasti ja vestluse nime.
        
        * https://www.geeksforgeeks.org/python-asksaveasfile-function-in-tkinter/
        * https://stackoverflow.com/questions/54305299/save-file-without-filedialog-in-pythontkinter
        '''
        files = [('CSV Files', '*.csv')] 
        file = filedialog.asksaveasfile(initialfile=f"FbMsg_{self.current_box}_{self.current_thread}.csv", filetypes = files, defaultextension = files, mode = 'w')
        if file is not None:
            file.write(self.T.get('1.0', 'end'))
            file.close()
            #self.T.insert(tk.END, f"\n Salvestamise asukoht: {file}\n")
            return True
        else:
            return False
        
    def key_exit(self):
        '''Lõpetamine''' 
        #self.myLogger('close()', "==========================")
        self.destroy()
    
    

        
        
   
    


if __name__ == "__main__":
    app = App()
    app.set_yt_api_key('AIzaSyC-rkBNmZ8kpH6N0Qfg-u1sDF3zdboMlZo')
    app.mainloop()
