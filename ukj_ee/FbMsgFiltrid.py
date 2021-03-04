# ukj@ukj.ee, 2021-02
# TODO: Kas filter lisatakse ilma kirjetele või filter eraldab/eemaldab kirjed?
#       Selle peaks lahendama iga filtri sees ja UI-ga
#       Vaikimisi võiks eraldada


import tkinter as tk
from tkinter import *

from ukj_ee.ytBasicMeta import ytBasicMeta

class FbMsgF_YouTubeTitles():
    yt=None
    yt_cache_path = ''
    yt_api_key = 'AIzaSyC-rkBNmZ8kpH6N0Qfg-u1sDF3zdboMlZo'
    filter_sel_state=None
    
    def __init__(self, cache):
        self.yt_cache_path = cache
        self.yt = ytBasicMeta(key=self.yt_api_key, cache=self.yt_cache_path)
        self.filter_sel_state = IntVar(value=1)
        
    def get_display_name(self):
        return 'YouTubeTitles'
        
    def display(self, parent):
        #if self.filter_sel_state:
        ytgroup = tk.LabelFrame(parent, padx=15, pady=10, text=self.get_display_name())
        Checkbutton(ytgroup, text='Aktiivsus',
            variable=self.filter_sel_state, onvalue=1,offvalue=0 ).pack(side=tk.LEFT)
        #Checkbutton(ytgroup, text='Kaasa|Eralda',
        #    variable=self.filter_union, onvalue=1,offvalue=0 ).pack(side=tk.LEFT)
        
        # print('FbMsgF_YouTubeTitles display() state: ', self.filter_sel_state.get())
        return ytgroup
    
    def switch(self):
        self.filter_sel_state = self.filter_sel_state if self.filter_sel_state.get()==1 else IntVar(value=0)
        
    def is_set(self):
        return self.filter_sel_state.get()
    
    
    def attachments(self, attachments):
        ''' YT lingiga manustes tiitli lisamine(True,[...]), teised asjad jäävad muutmata'''
        status = False

        if self.filter_sel_state.get()==0:
            return False, attachments
        
        result = []
        at = attype = yt_short = yt_title = yt_meta = ''
        for at in attachments:
            if isinstance(at, dict):
                for attype in at:
                    if attype == 'link' and 'youtu' in at[attype]:
                        yt_short = self.yt.get_shortUrl(at[attype])
                        if yt_short != '':
                            yt_meta = self.yt.get_meta_from_url(at[attype])
                            yt_title = yt_meta['title']

                        result.append({attype: yt_short +' '+yt_title } )
                        status = True
                    else:
                        result.append( {attype: at[attype]} )
                        
        return status, result




class FbMsgF_FindText():
    find_text_strv=None # = StringVar()
    
    part_sel_name=None # vormilt valitud nimi
    participants=None # täidetakse init ajal
    
    filter_sel_state=False
    
    def __init__(self):
        self.find_text_strv = tk.StringVar(value='')
        self.part_sel_name = tk.StringVar(value='')
        self.participants = []
        #print('FbMsgF_FindText __init__()')


    def get_display_name(self):
        return 'FindText'

    
    def set_participants(self, p):
        self.participants.append('')
        for pp in p:
            self.participants.append(pp)
        print('FbMsgF_FindText.set_participants(): ', p, ' kokku: ', self.participants)

        
    def display(self, parent):
        #if self.find_text_strv == None:
        findgroup = tk.LabelFrame(parent, padx=15, pady=10, text=self.get_display_name())
        
        #sataja nime valik, +'kõik==None'
        self.part_sel_name.set('') 
        tk.Label(findgroup, text='Osalised:').pack(side=tk.LEFT)
        opt = tk.OptionMenu( findgroup, self.part_sel_name, *self.participants)
        opt.config(width=13, font=('Helvetica', 12))
        opt.pack(side=tk.LEFT)
        
        #teksti otsing
        tk.Label(findgroup, text='Otsi:').pack(side=tk.LEFT)
        tk.Entry(findgroup, width=13, textvariable=self.find_text_strv).pack(side=tk.LEFT)
        return findgroup

    
    def is_set(self):
        self.filter_sel_state=len(self.find_text_strv.get()) > 0
        return self.filter_sel_state

    
    def message_time(self, timestamp):
        ''' aja otsingut veel pole'''  
        return True

    
    def sender_name(self, name):
        ''' Kes kirjutas, tuleb sõnumist'''
        if self.part_sel_name.get() == name:
            return True
        elif self.part_sel_name.get() == '':
            return True
        else:
            return False
 
    
    def content(self, msg):
        ''' Kontrollib üksikut sõnumit'''
        if self.find_text_strv.get() == '':
            return True
        if self.find_text_strv.get() in msg:
            return True
        
        return False





class FbMsgF_GenFilteringType():
    filter_type=None
    
    def __init__(self):
        self.filter_type=StringVar(value='Any')
        # print('FbMsgF_GenFilteringType __init__()')

    def get_display_name(self):
        return 'Fil. lisamise viis'
        
    def display(self, parent):  
        aagroup = tk.LabelFrame(parent, padx=15, pady=10, text=self.get_display_name())
        tk.Radiobutton(aagroup, text="Kõik, eraldamine", variable=self.filter_type, value='All').pack(side=tk.LEFT)
        tk.Radiobutton(aagroup, text="Ükski, lisamine", variable=self.filter_type, value='Any').pack(side=tk.LEFT)
        return aagroup
    
    def is_set(self):
        '''Alati olemas'''
        return True
    
    def general_filtering_type(self, results):
        ''' Kas kõik või Mõni'''
        if self.filter_type.get() == 'Any' and any(results):
            return True
        if self.filter_type.get() == 'All' and all(results):
            return True
        return False




class FbMsgF_to_CSV():
    def __init__(self):
        ''' '''
        # print('FbMsgF_to_CSV __init__()')
        
    def display_name(self):
        return 'CSV'
        
    def display(self, parent):
        return tk.Label(parent, text="CSV väljund")
    
    def is_set(self):
        return True
            
    def get_csv(self, conv):
        # print('FbMsgF_to_CSV get_csv()')
        csv = ''
        for rowid,row in conv.items():
            csv += row[0] +';'+ row[1] +';'+ row[2] +';'
            if len(row[3]) > 0:
                csv += 'Manused: \n'
                for at in row[3]:
                    for ty,ma in at.items():
                        csv += ';;;' +ty+ ':' +ma+ '\n'
            else:
                csv += '\n'
        return csv
