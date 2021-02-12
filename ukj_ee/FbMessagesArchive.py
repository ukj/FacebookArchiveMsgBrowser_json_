import json, re, os
from datetime import datetime
import zipfile
from zipfile import ZipFile #Kipub ise avatud zip faili sulgema 
# või kas tekib klassi objektist koopia millel fail on avamata?
# seeparast iga meetod avab faili ikkagi uuesti
# faili lugemine  with käsuga sulgeb ise



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
            #myLogger('set_ZipFp()', f"{FbArchiveZip}")
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
        #myLogger('load()', f"conv {conv_id}")
        conversation_with_name = None
        self.Zip_fp = ZipFile(self.Zip_f, 'r')
        with self.Zip_fp as zipObj:
            listOfiles = zipObj.namelist()
            for fileName in listOfiles:
                if fileName.endswith(".json") and fileName.startswith(f"messages/inbox/{conv_id}/message_"):
                    # zip to string
                    #myLogger('load()', f"fn {fileName}")
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
