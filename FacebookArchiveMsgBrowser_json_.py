import json, re, os
from datetime import datetime
import zipfile
from zipfile import ZipFile #Kipub ise avatud zip faili sulgema 
# või kas tekib klassi objektist koopia millel fail on avamata?
# seeparast iga meetod avab faili ikkagi uuesti
# faili lugemine  with käsuga sulgeb ise

import tkinter as tk
#from tkinter import font
from tkinter import filedialog
#from tkinter.filedialog import asksaveasfile
from tkinter.ttk import *

import yt_basicMeta, CreateToolTip

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


def myLogger(line, msg):
    with open("my-logger.txt", "a") as myfile:
        myfile.write("%s\t%s\t%s\n" % (datetime.timestamp(datetime.now()), line, msg)  )
    

class FbMessagesArchive:
    '''Loeb Facebooki arhiivist vestlusi ja manuseid; ukj@ukj.ee, 2021'''
    
    Zip_f = ''
    Zip_fp = None
    Conversation = []
    Metainfo = {}
    yt_cache_path=''
    
#    def __init__(self, FbArchiveZip=''):
#        if FbArchiveZip !='':
#            self.set_ZipFp(FbArchiveZip)
 
    def get_urls(self, text):
        '''
        Eraldab sõnumi tekstist urlid
        
        Parameters
        ----------
        text : str, mis sisaldab urle
        Returns
        -------
        list, urlid
        '''
        links_tmp = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text)
        return links_tmp
        
        
    def fb_reEncode(self, fbstr):
        '''
        Fb JSON kodeeringu probleem
        
        * https://stackoverflow.com/questions/12229064/mapping-over-values-in-a-python-dictionary
        * https://realpython.com/python-encodings-guide/
        
        Returns
        -------
        str
        '''
        for key in fbstr:
            if isinstance(fbstr[key], str):
                fbstr[key] = fbstr[key].encode('latin_1').decode('utf-8')
            
            elif isinstance(fbstr[key], list):
                fbstr[key] = list(map(lambda x: x if type(x) != str else x.encode('latin_1').decode('utf-8'), fbstr[key]))
            #pass
        return fbstr

        
    def set_ZipFp(self, FbArchiveZip):
        '''
        Avab arhiivi lugemiseks
        
        https://www.programcreek.com/python/example/2213/zipfile.is_zipfile
        * zipfile.is_zipfile(FbArchiveZip)
        * os.path.basename(FbArchiveZip.name).endswith('.zip')
        
        Parameters
        ----------
        FbArchiveZip : str, failitee
        Returns
        --------
        Bool
        '''
        
        if zipfile.is_zipfile(FbArchiveZip):
            print('is')
            self.Zip_f  = FbArchiveZip
            return True
        return False
    


    def is_loaded(self):
        if self.Zip_f != '':
            return True
        else:
            return False

    
    def get_threadBoxes(self):
        '''
        Kirjakastide nimekiri
        
        Returns
        -------
        list, inbox, archieved_threads
        '''
        threads = []
        self.Zip_fp = ZipFile(self.Zip_f, 'r')
        for f in self.Zip_fp.namelist():
            if f.startswith('messages/'):
                if f.endswith('_threads/') or f.endswith('inbox/'):
                    zinfo = self.Zip_fp.getinfo(f)
                    if(zinfo.is_dir()):
                        threads.append(f.split('/')[1])
        return threads
    

    def get_conversations(self, box='inbox'):
        '''
        Vestluste nimekiri
        
        Parameters
        ----------
        FbArchiveZip : str, inbox, archieved_threads
        Returns
        -------
        dict, nimed/id, {'idnimi':'fullid'} kelledega vestlusi on peetud
        
        * https://stackoverflow.com/questions/6510477/how-can-i-list-only-the-folders-in-zip-archive-in-python
        '''
        conv = {}
        self.Zip_fp = ZipFile(self.Zip_f, 'r')
        for f in self.Zip_fp.namelist():
            if f.startswith(f"messages/{box}/"):
                if f.count('/') == 3:
                    zinfo = self.Zip_fp.getinfo(f)
                    if(zinfo.is_dir()):
                        conv[f.split('/')[2].split('_')[0]] = f.split('/')[2]
        return conv




    def load_conversation(self, conv_id, own_name):
        '''
        Võtab ühe vestluse
                
        Vestluse osaliste nimede võtmine, mitme json läbimine
        https://masterscrat.github.io/Chatistics/
        MIT License
        
        * https://thispointer.com/python-how-to-get-the-list-of-all-files-in-a-zip-archive/
        * https://thispointer.com/python-how-to-unzip-a-file-extract-single-multiple-or-all-files-from-a-zip-archive/
        
        Parameters
        ----------
        FacebookArchiveZip : str, failitee
        conversation_id : str, box/vestlus
        own_name : str, Enda nimi
        Returns
        -------
        list, mitmemõõtmeline list [vestlus [timestamp, sender_name, content, [attachments {type:content}] ]]
        '''
        self.Metainfo = {'conv_id':'','host':'','participants':[]}
        self.Conversation = []
        myLogger('load()', f"conv {conv_id}")
        conversation_with_name = None
        self.Zip_fp = ZipFile(self.Zip_f, 'r')
        with self.Zip_fp as zipObj:
            listOfiles = zipObj.namelist()
            for fileName in listOfiles:
                if fileName.endswith(".json") and fileName.startswith(f"messages/inbox/{conv_id}/message_"):
                    # zip to string
                    myLogger('load()', f"fn {fileName}")
                    a_file = zipObj.read(fileName)
                    #a_file = self.fb_reEncode(a_file) 
                    json_data = json.loads(a_file, object_hook=self.fb_reEncode)
                    
                    # TODO: Mitme vestluskaaslase käsitlemine ja sõnumite lugemine kui kaaslaste nimekiri puuduks aga vestlus siiski on, kas saab nii olla?
                    if "messages" not in json_data or "participants" not in json_data: continue
                    participants = json_data["participants"]
                    if len(participants) > 2: continue
                    
                    
                    for participant in participants:
                        if participant['name'] != own_name:
                            conversation_with_name = participant['name']
                        if conversation_with_name is None:
                            conversation_with_name = conv_id
                        self.Metainfo['participants'].append(conversation_with_name)
                    self.Metainfo['conv_id'] = conv_id
                    self.Metainfo['host'] = own_name
                    
                    for message in json_data["messages"]:
                        timestamp_ms = int(message["timestamp_ms"])
                        content = ''
                        attachments = []
                        if "content" in message and "sender_name" in message:
                            content = message["content"]
                            if "sender_name" in message:
                                sender_name = message["sender_name"]
                            else:
                                sender_name = conv_id
                            #outgoing = sender_name == own_name
                            
                            if 'content' in message:
                                content = message['content']
                                for file in self.get_urls(content):
                                    file = file.strip()
                                    if file != '':
                                        attachments.append({'link':file})
                            
                            if 'photos' in message:
                                for file in message['photos']:
                                    attachments.append({'photo':file['uri']})
                                    #attachments['photo']=file['uri']
                            
                            if 'sticker' in message:
                                attachments.append({'sticker':message['sticker']['uri']})
                            
                            if 'audio_files' in message:
                                for file in message['audio_files']:
                                    attachments.append({'audio':file['uri']})
                                    #attachments['audio']=file['uri']
                            
                            if 'videos' in message:
                                for file in message['videos']:
                                    attachments.append({'video':file['uri'], 'thumbnail':file['thumbnail']['uri']})
                                  
                            if 'files' in message:
                                for file in message['files']:
                                    attachments.append({'file':file['uri']})
                            
                            if 'Share' in message:
                                attachments.append({'link':message['share']['link']})
                                 
                            self.Conversation.append([timestamp_ms, sender_name, content, attachments ])
                            #if len(data) >= MAX_EXPORTED_MESSAGES:
                                #log.warning(f'Reached max exported messages limit of {MAX_EXPORTED_MESSAGES}. Increase limit in order to parse all messages.')
                                #return data


    def get_conversation_filtered(self, filter='', yt=None):
        #print(self.Conversation)
        
        if(filter==''):
            return self.Conversation
        f_ytmeta = True if 'ytmeta' in filter and isinstance(yt, object) else False
            
        # TODO: Split filter def, attatchments, numbers, dates, email ,ytmeta
         
        result = []
        for i in range(len(self.Conversation)):
            if len(self.Conversation[i][2]) > 0 and len(self.Conversation[i][3]) > 0:
                #print(self.Conversation[i])
                Saatja = self.Conversation[i][1]
                Aeg = datetime.utcfromtimestamp(int(self.Conversation[i][0]/1000)).strftime('%Y-%m-%d %H:%M:%S')
                Sonum = self.Conversation[i][2]
                #Manused = self.Conversation[i][3]
                
                result.append("%s;%s;\"%s\";;;" % (Saatja, Aeg, Sonum ))
                
                at=attype=yt_short=yt_title=yt_meta=''
                for at in self.Conversation[i][3]:
                    if isinstance(at, dict): 
                        for attype in at:
                            if attype=='link' and 'youtu' in at[attype]:
                                yt_short = yt.get_shortUrl(at[attype])
                                if yt_short != '':
                                    
                                    if f_ytmeta:
                                        yt_meta = yt.get_meta_from_url(at[attype])
                                        yt_title = yt_meta['title']
                                        #yt_title = '!!!'
                                    else:
                                        yt_title = ''
                                    
                                result.append(";;;%s;%s;\"%s\"" % (attype, yt_short, yt_title))
                            else:
                                result.append(";;;%s;%s;\"\"" % (attype, at[attype]))
        return result    











own_name='Nimi'
yt = yt_basicMeta.yt_basicMeta('AIzaSyC-rkBNmZ8kpH6N0Qfg-u1sDF3zdboMlZo')
yt.set_cache_file('yt_basicMeta.sqlite')
fbmsg = FbMessagesArchive()
current_box = current_thread = ''
result = []
msg_boxes = []
msg_convs = []



def dict_keys(d):
    k = []
    for i in d: 
        k.append(i)
    return k

def textbox_clear():
    global T
    T.tag_add('sel', '1.0', 'end')
    T.delete(1.0, 'end')
    root.update()
    T.tag_remove('sel', '1.0', 'end')
    

        
def textselect(parent,textwidget):
    parent.event_generate("<<TextModified>>")
    textwidget.focus()
    textwidget.tag_add('sel', '1.0', 'end')


def textbox_copy():
    '''
    * https://mail.python.org/pipermail/tutor/2004-July/030398.html
    * https://stackoverflow.com/questions/64251762/python-tkinter-select-and-copy-all-text-contents-to-clipboard-on-button-clic
    * https://stackoverflow.com/questions/20611523/tkinter-text-widget-unselect-text
    '''
    global root, T
    root.clipboard_clear()
    T.focus()
    T.event_generate("<<TextModified>>")
    T.tag_add('sel', '1.0', 'end')   
    root.clipboard_append( T.get("sel.first", "sel.last") )
    root.update()
    T.tag_remove('sel', '1.0', 'end')

def selistbox_Box(event):
    global T, listbox_Box, fbmsg, msg_convs, own_name, yt, current_box, current_thread
    anchor=str( listbox_Box.get(tk.ANCHOR) )
    selection=event.widget.curselection()
    if selection:
        index = selection[0]
        value = event.widget.get(index)
    elif anchor:
        value=anchor 
    else:
        value='inbox'

    if fbmsg.is_loaded() is False:
        return False
    
    listbox_Thread.delete(0, 'end') 
    fbmsg.get_threadBoxes() #msg_boxes =
    msg_convs = fbmsg.get_conversations(value)
    persons =   dict_keys(msg_convs)
    value=''
    if len(persons) > 0:
        p1 = persons[0]
        first_thread = msg_convs[p1]
        for element in msg_convs:
            listbox_Thread.insert(tk.END,element)
           
        listbox_Thread.selection_set( first = 0 )
        listbox_Thread.select_set(0) #This only sets focus on the first item.
        listbox_Thread.event_generate("<<ListboxSelect>>")
    
        fbmsg.load_conversation(first_thread , own_name)
        result = fbmsg.get_conversation_filtered('attachments ytmeta', yt)
        current_box = value
        current_thread = p1
        
        textbox_clear()
        myLogger('box()', f"box 1 thr {first_thread}\n\n {p1}\n{persons} \n\n{msg_convs}")
        T.insert(tk.END, f"\n f thr {first_thread}\n")
        T.insert(tk.END, f"\n box {value}\n\n{first_thread}\n{msg_convs}")
        T.insert(tk.END, "\n".join(result))
    

def selistbox_Thread(event):
    global tk, T ,listbox_Thread, msg_convs, fbmsg, own_name, yt, current_box, current_thread
    anchor=str(listbox_Thread.get(tk.ANCHOR))
    selection=event.widget.curselection()
    value=''
    if selection:
        index = selection[0]
        value = event.widget.get(index)
    elif anchor:
        value=anchor    
    
    if value != '':
        #persons = dict_keys(msg_convs)
        thread = msg_convs[ value ]
        msg_boxes = fbmsg.get_threadBoxes()
        
        fbmsg.load_conversation(thread, own_name)
        result = fbmsg.get_conversation_filtered('attachments ytmeta', yt)
        current_box = 'inbox'
        current_thread = value
            
        myLogger('thread()', "tyhj")
        textbox_clear()
        T.insert(tk.END, f"\n thread {value} {thread}\n\n\n")
        T.insert(tk.END, "\n".join(result))
        myLogger('thread()', "res")

    
        
def key_openfile():
    '''
    * https://www.geeksforgeeks.org/python-askopenfile-function-in-tkinter/
    '''
    global T, tk, fbmsg, msg_boxes, msg_convs, own_name, result, yt, current_box, current_thread
    files = [('Zip Files', '*.zip')]
    file = filedialog.askopenfilename(filetypes = files, defaultextension = files)
    print(1)
    try:
        isf = os.path.isfile(file)
    except:
        isf = False
        
    if isf:
        print(2)
        if fbmsg.set_ZipFp(file): 
            print(3)
            listbox_Box.delete(0,tk.END)
            listbox_Thread.delete(0,tk.END)
                       
            msg_boxes = fbmsg.get_threadBoxes()
            msg_convs = fbmsg.get_conversations('inbox')
            
            persons =   dict_keys(msg_convs)
            p1 = persons[0]
            thread = msg_convs[p1]
            for element in msg_boxes:
                listbox_Box.insert(tk.END,element)
            myLogger('open()', f"convs {p1}\n{persons}\n\n")    
            listbox_Box.selection_set( first = 0 )
            listbox_Box.select_set(0) #This only sets focus on the first item.
            listbox_Box.event_generate("<<ListboxSelect>>")
            
            for element in msg_convs:
                listbox_Thread.insert(tk.END,element)
            listbox_Thread.selection_set( first = 0 )
            listbox_Thread.select_set(0) #This only sets focus on the first item.
            listbox_Thread.event_generate("<<ListboxSelect>>")
            myLogger('open()', f"convs {msg_convs}")
                    
            fbmsg.load_conversation(thread , own_name)
            result = fbmsg.get_conversation_filtered('attachments ytmeta', yt)
            current_box = 'inbox'
            current_thread = p1
            
            textbox_clear()
            T.insert(tk.END, f"\n Fb zip asukoht: {file}\n")
            T.insert(tk.END, f"\n Kastid: {msg_boxes}\n\nThread {thread}\n\n Inimesed: {msg_convs}\n")
            T.insert(tk.END, "\n".join(result))
        else:
            result = []
            
    

def key_savefile():
    '''
    * https://www.geeksforgeeks.org/python-asksaveasfile-function-in-tkinter/
    * https://stackoverflow.com/questions/54305299/save-file-without-filedialog-in-pythontkinter
    '''
    global tk, T, own_name, current_box, current_thread
    files = [('CSV Files', '*.csv')] 
    file = filedialog.asksaveasfile(initialfile=f"FbMsg_{current_box}_{current_thread}.csv", filetypes = files, defaultextension = files, mode = 'w')
    if file is not None:
        file.write(T.get('1.0', 'end'))
        file.close()
        #T.insert(tk.END, f"\n Salvestamise asukoht: {file}\n")
    
def key_exit():
    global tk, root 
    myLogger('close()', "==========================")
    root.destroy()


class key_helpWindow(tk.Toplevel):
    '''
    *  https://www.geeksforgeeks.org/open-a-new-window-with-a-button-in-python-tkinter/
    '''      
    def __init__(self, parent): 
        super().__init__(parent)
        self.geometry('400x400') 
        text_title="Help for Facebook Archive msg JSON"
        text = f"""
\t{text_title}
\t--- --- --- --- --- --- --- --- --- --- --- --- --- ---

* Loeb zip faili ilma kõike lahti pakkimata
* Filtreeritud teksti saab kopeerida lõikelauale või salvestada CSV
* Näitab manuste failiteesid ja tekstis leiduvaid linke
* Lisab Youtube JSON API-t kasutades video linkidele 
    pealkirjad ja salvestab need SQLite abil.

Ava            Ctrl-O
Salv            Ctrl-S
Kopeeri kõik    Ctrl-Alt-C
Tühjenda        Ctrl-E
Välju           Ctrl-Q või Alt-F4
Abi            Ctrl-H või F1


\tukj@ukj.ee, 2021.02"""
        
        self.title(text_title)
        label = Label( self, text=text, relief=tk.RAISED, wraplength=scw)
        label.pack()
    
    
#courier14 = tkFont.Font(family="Courier",size=14,weight="bold")       
root = tk.Tk()
root.title("Facebooki Sõnumite Arhiiv")

scw = 700
sch = 700
root.geometry(f"{scw}x{sch}")
root.resizable(True, True) #Don't allow resizing in the x or y direction


S = tk.Scrollbar(root)

T = tk.Text(root, height=4, width=50)
#T.insert(tk.END, font.nametofont("TkFixedFont").actual())
#T.insert(tk.END, "\n".join(result))
S.config(command=T.yview)
T.config(yscrollcommand=S.set, state=tk.NORMAL)

# will work nicely and use the system default monospace font
#fixed = ttk.Style()
#fixed.configure('Fixed.TButton', font='TkFixedFont', size=14)

group_1 = tk.LabelFrame(root, padx=15, pady=10, text="Toimingud")

# https://www.plus2net.com/python/tkinter-listbox.php
# https://www.geeksforgeeks.org/scrollable-listbox-in-python-tkinter/
# https://tk-tutorial.readthedocs.io/en/latest/listbox/listbox.html

listbox_Box = tk.Listbox(group_1,height=3, selectmode='browse', selectbackground='blue',highlightcolor='yellow',highlightthickness=1)
listbox_Box.bind('<<ListboxSelect>>', selistbox_Box)
listboxScroll_Box = tk.Scrollbar(group_1)
listbox_Box.config(yscrollcommand = listboxScroll_Box.set)
listboxScroll_Box.config(command = listbox_Box.yview)

listbox_Thread = tk.Listbox(group_1,height=3, selectmode='browse',selectbackground='blue',highlightcolor='yellow',highlightthickness=1)
listboxScroll_Thread = tk.Scrollbar(group_1)
listbox_Thread.config(yscrollcommand = listboxScroll_Thread.set)
listboxScroll_Thread.config(command = listbox_Thread.yview)
listbox_Thread.bind('<<ListboxSelect>>', selistbox_Thread)

button_fileopen = tk.Button(group_1, text="Ava", command=key_openfile)
button_filesave = tk.Button(group_1, text="Salv. CSV", command=key_savefile)
button_copy = tk.Button(group_1, text='Kopeeri', command=textbox_copy)
button_clear = tk.Button(group_1, text='Tühj.', command=textbox_clear)
button_exit = tk.Button(group_1, text='X', command=key_exit)
button_help = tk.Button(group_1, text='?', command=key_helpWindow(group_1))

'''
CreateToolTip.CreateToolTip(root, button_fileopen, "Ava arhiiv zip Ctrl+O")
CreateToolTip.CreateToolTip(root, button_filesave, "Salvesta filtreering tekstina Ctrl+S")
CreateToolTip.CreateToolTip(root, button_copy, "Kopeeri kõik Ctrl+Alt+C")
CreateToolTip.CreateToolTip(root, button_clear, "Tühjenda Ctrl+E")
CreateToolTip.CreateToolTip(root, listbox_Box, "Vesluste sahtlid")
CreateToolTip.CreateToolTip(root, listbox_Thread, "Vestlused")
CreateToolTip.CreateToolTip(root, button_exit, "Lõpeta Ctrl+Q või Alt+F4")
CreateToolTip.CreateToolTip(root, button_help, "Teave Ctrl+H või F1")
'''

root.bind("<Control-o>", key_openfile)
root.bind("<Control-s>", key_savefile)
root.bind("<Control-Alt-c>", textbox_copy)
root.bind("<Control-E>", textbox_clear)
root.bind("<Control-q>", key_exit)
root.bind("<Alt-F4>", key_exit)
#root.bind("<Control-h>", key_helpWindow(group_1))
#root.bind("<F1>", key_helpWindow(group_1))




button_fileopen.pack(side=tk.LEFT)
button_filesave.pack(side=tk.LEFT)
listbox_Box.pack(side=tk.LEFT)
listboxScroll_Box.pack(side = tk.LEFT, fill = tk.BOTH)
listbox_Thread.pack(side=tk.LEFT)
listboxScroll_Thread.pack(side = tk.LEFT, fill = tk.BOTH)
#button_insert.pack(side=tk.LEFT)
button_copy.pack(side=tk.LEFT)
button_clear.pack(side=tk.LEFT)
button_help.pack(side=tk.LEFT)
button_exit.pack(side=tk.LEFT)
group_1.pack()

T.pack(expand=tk.YES, side=tk.LEFT, fill=tk.BOTH)
S.pack(side=tk.RIGHT, fill=tk.Y)

root.update()
tk.mainloop()
