# Facebooki arhiivi lehitseja
# ukj@ukj.ee, 2021


import os
import tkinter as tk
from tkinter import filedialog, messagebox

os.chdir(os.path.dirname( os.path.abspath(__file__) ))

import thirdparty.CreateToolTip
from ukj_ee.FbMessagesArchive import *
#from ukj_ee.yt_basicMeta import yt_basicMeta

class AppHelpWindow(tk.Toplevel):
    '''Abiaken
    
    * https://www.geeksforgeeks.org/open-a-new-window-with-a-button-in-python-tkinter/
    * https://www.askpython.com/python/examples/find-all-methods-of-class
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
* Lisab Youtube JSON API-t kasutades video linkidele pealkirjad
    ja salvestab need SQLite abil.

\tKiirklahvid
Ava zip\t\tCtrl-O
Salv csv\t\tCtrl-S
Kopeeri kõik\tCtrl-Alt-C
See abi\t\tCtrl-H
Välju\t\tCtrl-Q

\tukj@ukj.ee, 2021.02"""
        
        self.title(text_title)
        label = Label( self, text=text, relief=tk.RAISED, wraplength=600)
        label.pack()   
        self.update()
        scw = int(self.winfo_width()/2) # int(self.winfo_screenwidth()/4)
        
        w=int(self.winfo_width())
        h=int(self.winfo_height())

        self.geometry(f"{w}x{h}+{scw}+220")
        self.update()

        



class ScrollableFrame(tk.Frame):
    def __init__(self, master, **kwargs):
        tk.Frame.__init__(self, master, **kwargs)
        '''
        * https://stackoverflow.com/questions/23483629/dynamically-adding-checkboxes-into-scrollable-frame
        '**' takes a dict and extracts its contents and passes them as parameters to a function
        *args extracts positional parameters and **kwargs extract keyword parameters.
        * https://treyhunner.com/2018/10/asterisks-in-python-what-they-are-and-how-to-use-them/
        '''

        # create a canvas object and a vertical scrollbar for scrolling it
        self.vscrollbar = tk.Scrollbar(self, orient=tk.VERTICAL)
        self.vscrollbar.pack(side='right', fill="y",  expand="false")
        #print(self.__name__)
        self.canvas = tk.Canvas(self, bd=0, height=400, width=460,
                                highlightthickness=0,
                                yscrollcommand=self.vscrollbar.set)
        self.canvas.pack(side="left", expand="true")
        self.vscrollbar.config(command=self.canvas.yview)

        # reset the view
        self.canvas.xview_moveto(0)
        self.canvas.yview_moveto(0)

        # create a frame inside the canvas which will be scrolled with it
        self.interior = tk.Frame(self.canvas, **kwargs)
        self.canvas.create_window(0, 0, window=self.interior, anchor="nw")

        self.bind('<Configure>', self.set_scrollregion)
    
    def update_geomerty(self, height=400, width=460):
        self.canvas.configure(height=height, width=width)
        
        
    def set_scrollregion(self, event=None):
        """ Set the scroll region on the canvas"""
        self.canvas.configure(scrollregion=self.canvas.bbox('all'))



class App(tk.Tk):
    ''' Rakenduse peaaken'''
    #   Kujundid
    frame=None
    csw = csh = 700
    listbox_Box=None
    listbox_Thread=None
    T=None    
    appButtons = {}   
    ctlrKeys = {}
    
    #   Andmed
    yt_cache = ''
    fbmsg = FbMessagesArchive()
    msg_boxes = []
    msg_convs = []
    conv_loaded = False
    current_box = ''
    current_thread = ''
    own_name='Nimi'
    filter_result = []

    def __init__(self):
        '''Peaaknaga alustamine
        
        * https://www.plus2net.com/python/tkinter-listbox.php
        * https://www.geeksforgeeks.org/scrollable-listbox-in-python-tkinter/
        * https://tk-tutorial.readthedocs.io/en/latest/listbox/listbox.html
        * https://www.codershubb.com/bind-mouse-button-click-event-with-tkinter-listbox-in-python/
        * https://www.delftstack.com/howto/python-tkinter/how-to-change-tkinter-button-state/
        
        '''
        super().__init__()
        
        self.scw = self.sch = 700
        self.title("Facebooki Sõnumite Arhiiv")
        self.resizable(True, True) #Suurus muudetav suunal X Y        
        self.frame = tk.Frame(self, height = self.scw, width = self.sch)
        self.frame.pack()
        self.update()
        
        
        S = tk.Scrollbar(self.frame)
        self.T = tk.Text(self.frame, height=50, width=80)        
        S.config(command=self.T.yview)
        self.T.config(yscrollcommand=S.set, state=tk.NORMAL)
        
        #   Asjade hoidja
        group_1 = tk.LabelFrame(self.frame, padx=15, pady=10, text="Toimingud")
            
        self.listbox_Box = tk.Listbox(group_1,height=3, width=14, selectmode='browse', selectbackground='blue',highlightcolor='yellow',highlightthickness=1) 
        listboxScroll_Box = Scrollbar(group_1)
        self.listbox_Box.config(yscrollcommand = listboxScroll_Box.set) 
        listboxScroll_Box.config(command = self.listbox_Box.yview)
        self.listbox_Box.bind('<<ListboxSelect>>', self.listboxSel_Box)
        
        self.listbox_Thread = tk.Listbox(group_1,height=3, width=14 ,selectmode='browse',selectbackground='blue',highlightcolor='yellow',highlightthickness=1)
        listboxScroll_Thread = Scrollbar(group_1)
        self.listbox_Thread.config(yscrollcommand = listboxScroll_Thread.set)
        listboxScroll_Thread.config(command = self.listbox_Thread.yview)
        self.listbox_Thread.bind('<<ListboxSelect>>', self.listboxSel_Thread)
        
        #   Nuppude loomine ja Töövahendite järjestamine
        self.AppButton_create(group_1, 'fileOpen', 'Ava',self.key_openfile, text_tooltip='Ava arhiiv zip', controlkey='o') # keysym=o keycode=79 char='\x0f' 
        self.AppButton_create(group_1, 'fileSave', 'Salv\nCSV',self.key_savefile, text_tooltip='Salvesta filtreering tekstina', controlkey='s') # keysym=s keycode=83 char='\x13'     
        self.AppButton_create(group_1, 'copyAll', 'Kopeeri',self.textbox_copy, text_tooltip='Kopeeri kogu see vestlus', controlkey='c')# keysym=c keycode=67 char='\x03' 
        self.AppButton_create(group_1, 'filSelector', 'Filt.',self.filter_selector_window, text_tooltip='Ava filtrite valik', controlkey='')
        self.appButtons['filSelector']['state']=tk.DISABLED
        
        self.listbox_Box.pack(side=tk.LEFT)
        listboxScroll_Box.pack(side = tk.LEFT, fill = tk.BOTH)

        self.listbox_Thread.pack(side=tk.LEFT)
        listboxScroll_Thread.pack(side = tk.LEFT, fill = tk.BOTH)
        
        self.AppButton_create(group_1,'helpWin',' ? ',self.key_helpWindow, text_tooltip='Salvesta filtreering tekstina', controlkey='h')#keysym=h keycode=72 char='\x08'
        self.AppButton_create(group_1,'exitApp',' X ', self.key_exit, text_tooltip='Lõpeta', controlkey='q')#keysym=q keycode=81 char='\x11'
        group_1.pack()

        self.T.pack(expand=tk.YES, side=tk.LEFT, fill=tk.BOTH)
        S.pack(side=tk.RIGHT, fill=tk.Y)
        self.update()
        
        #   Akna suuruse täpsustamine   
        #self.sch = int(self.winfo_screenheight()-120) #õige , aga vahel aken liiga suur, suurem kui tekstikast
        #h = int(self.winfo_screenheight()-200)
        self.scw = self.winfo_width()
        self.sch = self.winfo_height()
        self.frame.config(width=self.scw, height=self.sch)
        self.geometry(f"{self.scw}x{self.sch}")
        self.update()
        #print(self.ctlrKeys)
        #self.mainloop()
        #myLogger('App.__init__()', " end") 

        
        
        
        
        
        
    def AppButton_create(self, group, name, text,cmd,  text_tooltip='', controlkey=''):
        '''Nuppude tegija
        
        * https://www.daniweb.com/programming/software-development/threads/111526/setting-a-string-as-a-variable-name
        * https://stackoverflow.com/questions/50615371/accessing-tkinter-buttons-found-in-a-dictionary
        * https://stackoverflow.com/questions/16082243/how-to-bind-ctrl-in-python-tkinter
        * #exec("%s = %d" % (name, 2))
        * food = 'bread'; vars()[food] = 123; print bread  # --> 123
        * vars(self)['a'] = 10; print(self.a)
        '''
        bw =2
        if "\n" in text:
            bw=len(text.split("\n")[0])
        else:
            bw=len(text)
        
        b = tk.Button(group, text=text, padx=3, command=cmd, width=bw)
        
        if text_tooltip != '':
            if controlkey != '':
                text_tooltip +=  ' Ctrl+' + controlkey.title() 
            thirdparty.CreateToolTip.CreateToolTip(self, b, text_tooltip)
        
        if controlkey != '':
            self.ctlrKeys[controlkey] = cmd.__name__
            self.frame.bind_all( '<Control-'+controlkey+'>', self.AppButton_ctrlKey)

        b.pack(side=tk.LEFT)
        b.config(width=bw, height=2)
        self.appButtons[name] = b
        self.update()

    def AppButton_update(self, name, text):
        '''Nupu kirja muutmine'''
        self.appButtons[name].configure(text=text)

    
    def AppButton_ctrlKey(self, event):
        '''
        * https://stackoverflow.com/questions/19861689/check-if-modifier-key-is-pressed-in-tkinter#19863837
        mods = {
            0x0001: 'Shift',
            0x0002: 'Caps Lock',
            0x0004: 'Control',
            0x0008: 'Left-hand Alt',
            0x0010: 'Num Lock',
            0x0080: 'Right-hand Alt',
            0x0100: 'Mouse button 1',
            0x0200: 'Mouse button 2',
            0x0400: 'Mouse button 3'
        }
        '''
        if event.state==4:
            if self.ctlrKeys[event.keysym] in dir(self):
                exec("self.%s()" % self.ctlrKeys[event.keysym])







              
    
    
    
    
    
    
    
    
    

    filter_sel_win=None
    filter_sel_boxes={}
    filter_sel_states={}
    
    def filter_selector_update(self, event):
        # print('filter_selector_update()')
        if self.conv_loaded == False:
            return False
        
        if self.filter_sel_win.winfo_exists()==False:
            self.refilter_thread()
        if self.filter_sel_win.winfo_exists():
            self.refilter_thread()
            
            
        
            
    def filter_selector_window(self):
        '''Filtrite/Pluginate paan
        
        # https://stackoverflow.com/questions/52950267/tkinter-frame-in-toplevel-displayed-in-parent
        # https://stackoverflow.com/questions/23483629/dynamically-adding-checkboxes-into-scrollable-frame
        # https://www.plus2net.com/python/tkinter-checkbutton.php
        # https://www.geeksforgeeks.org/python-setting-and-retrieving-values-of-tkinter-variable/
        # https://www.delftstack.com/howto/python-tkinter/how-to-hide-recover-and-delete-tkinter-widgets/
        '''
        
        if self.conv_loaded == False:
            return False
        
        ''' Ilma raamita aken, nagu kollased teated, 
        kohandub valikute arvuga '''
        
        
        if isinstance(self.filter_sel_win, tk.Toplevel):
            try:
                self.filter_sel_win.deiconify()
                return True
            except Exception:
                self.filter_sel_win=None
                pass
            
        
        
        self.filter_sel_win = tk.Toplevel(self.frame)
        self.filter_sel_win.title('Filtrid')
        
        #   Akna kuju ja asukoht
        # self.filter_sel_win.wm_overrideredirect(True) # Raami eemaldaja
        x=y=0
        sch = int(self.appButtons['filSelector'].winfo_height())
        x += self.appButtons['filSelector'].winfo_rootx() + 0
        y += self.appButtons['filSelector'].winfo_rooty() + sch      
        self.filter_sel_win.geometry("400x400+%d+%d" % (x, y))
        #self.filter_sel_win.wm_geometry("+%d+%d" % (x, y))
        self.filter_sel_win.configure(borderwidth=2, relief="solid", padx=3, pady=3)        
        #   Keritav raam
        self.checkbox_pane = ScrollableFrame(self.filter_sel_win)
        self.checkbox_pane.pack(side=tk.LEFT)
        filter_row=0
        b = tk.Button(self.checkbox_pane.interior, text='Kinnita', padx=1, command=self.refilter_thread, width=6)
        b.config(width=6, height=1)
        b.grid(row=filter_row, column=0, padx=(5, 5),pady=(2, 2), sticky=tk.W+tk.E)
        thirdparty.CreateToolTip.CreateToolTip(self.checkbox_pane, b, 'Kinnita muutused')
    
        #   Iga filtri UI asub selle klassis
        filter_row=1
        for filter_sel_st_name in self.fbmsg.get_filter_names():
            self.fbmsg.get_filter_display(filter_sel_st_name, self.checkbox_pane.interior).grid(row=filter_row, 
                                column=0, padx=(5, 5),pady=(2, 2), sticky=tk.W+tk.E)
            filter_row += 1
        
        #self.filter_sel_states['FbMsgF_YouTubeTitles'].set(1)
        self.checkbox_pane.interior.update()
        
        #   Suuruse täpsustamine pärast sisu valmistamist
        self.checkbox_pane.interior.columnconfigure(0, weight=1)
        w=int(self.checkbox_pane.interior.winfo_width()+50)
        h=int(self.checkbox_pane.interior.winfo_height()+10)
        if h > self.frame.winfo_height():
            h = self.frame.winfo_height()-80
        self.filter_sel_win.geometry("%dx%d+%d+%d" % (w, h, x, y))
        self.filter_sel_win.update()
        self.checkbox_pane.focus_set()

             
                


    
    def refilter_thread(self, value=''):
        '''
        value:str vestluskaaslase nimi_id
        '''
        #print('refilter_thread() msg_convs:', self.msg_convs)
        # print('refilter_thread() value:', value)
        if value != '':
            if self.current_thread == value:
                self.conv_loaded = True
            else:
                self.conv_loaded = False
                self.current_thread = value
        
        # v2='' 
        if value=='':
            if self.current_thread == '':
                for value, v2 in self.msg_convs.items():
                    self.current_thread = value
                    break
                self.conv_loaded = False
            else:
                value = self.current_thread
                self.conv_loaded = True
        
        # print('refilter_thread() ', 'conv_loaded:',self.conv_loaded, 'value|v2:',value,':', v2,'cur: ',self.current_thread)
        
        if self.conv_loaded == False:
            self.current_thread = self.msg_convs[value]
            self.fbmsg.load_conversation(self.current_thread, self.own_name)
            self.appButtons['filSelector']['state']=tk.NORMAL
            self.conv_loaded = True
        
        self.fbmsg.conversation_filtering()
        self.filter_result = self.fbmsg.get_conversation_CSV() 
        self.T.delete('1.0',"end-1c")
        self.T.update()
        self.T.insert(tk.END, f"\n Kirjakast: {self.current_box}\nVestlus: {self.current_thread}\n\n")
        self.T.insert(tk.END, "\n"+self.filter_result)
    
    
    
    
    
    def listboxSel_Thread(self, event):
        anchor=str(self.listbox_Thread.get(tk.ANCHOR))
        selection=event.widget.curselection()
        value=''
        if selection:
            index = selection[0]
            value = event.widget.get(index)
        elif anchor:
            value=anchor    
        
        # print('listboxSel_Thread() value:', value)
        self.refilter_thread(value)                



    def listboxSel_Box(self, event):
        '''kirjakasti valimisel valitakse eaimene vestlus'''
        
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
        
        self.current_box = value      
        self.listbox_Thread.delete(0, 'end') 
        self.fbmsg.get_threadBoxes() #msg_boxes =
        self.msg_convs = self.fbmsg.get_conversations(value)
            
        persons = [p for p in self.msg_convs]
        if len(persons) > 0:
            #p1 = persons[0]
            #first_thread = self.msg_convs[p1]
            for element in self.msg_convs:
                self.listbox_Thread.insert(tk.END,element)
            
            self.T.delete('1.0',"end-1c")
            self.T.update()       
            self.T.insert(tk.END, f"\n Kirjakast {value}\n\n")
        
            self.listbox_Thread.select_set(0) #This only sets focus on the first item.
            self.listbox_Thread.select_set(first=0)
            self.listbox_Thread.event_generate("<<ListboxSelect>>")
            #print('listboxSel_Box() ', self.msg_convs, value) 
    
    
    
    
    
    
    
    def key_helpWindow(self):
        window = AppHelpWindow(self)
        window.grab_set()
        

    
    def key_openfile(self):
        '''Faili avamisel avatakse 'inbox'i esimene vestlus
        
        * https://www.geeksforgeeks.org/python-askopenfile-function-in-tkinter/
        * https://runestone.academy/runestone/books/published/thinkcspy/GUIandEventDrivenProgramming/02_standard_dialog_boxes.html
        '''
        
        files = [('Zip Files', '*.zip')]
        file = filedialog.askopenfilename(filetypes = files, defaultextension = files)
        try:
            isf = os.path.isfile(file)
        except:
            isf = False
            
        if isf:
            if self.fbmsg.set_ZipFp(file):
                
                self.filter_result = []
                #messagebox.showinfo("Teave",f"Youtubest teabe hankimine võib kaua aega võtta.")
                
                # Fb arhiivi kõrval
                self.fbmsg.set_yt_cache_path( os.path.splitext(file)[0]+'.yt.sqlite' )
                self.listbox_Box.delete(0,tk.END)
                self.listbox_Thread.delete(0,tk.END)
                     
                self.msg_boxes = self.fbmsg.get_threadBoxes()
                self.msg_convs = self.fbmsg.get_conversations('inbox')
                
                for element in self.msg_boxes:
                    self.listbox_Box.insert(tk.END,element)
                
                self.T.delete('1.0',"end-1c")
                self.T.update()
                self.listbox_Box.select_set(0) #vali esimene
                self.listbox_Box.select_set(first=0)
                self.listbox_Box.event_generate("<<ListboxSelect>>")
                
            else:
                self.filter_result = []
                
        
    
    
    
    
    
    
    
    
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
        # print('key_exit()')
        self.destroy()
           
    def textselect(self, parent,textwidget):
        parent.event_generate("<<TextModified>>")
        textwidget.focus()
        textwidget.tag_add('sel', '1.0',  "end-1c")

    
    def textbox_copy(self):
        '''
        * https://mail.python.org/pipermail/tutor/2004-July/030398.html
        * https://stackoverflow.com/questions/64251762/python-tkinter-select-and-copy-all-text-contents-to-clipboard-on-button-clic
        * https://stackoverflow.com/questions/20611523/tkinter-text-widget-unselect-text
        '''
        self.clipboard_clear()
        self.T.focus()
        self.T.event_generate("<<TextModified>>")
        self.T.tag_add('sel', '1.0',  "end-1c")   
        self.clipboard_append( self.T.get("sel.first", "sel.last") )
        self.update()
        self.T.tag_remove('sel', '1.0',  "end-1c")
    
        
        
   
    


if __name__ == "__main__":
    app = App()
    app.mainloop()
