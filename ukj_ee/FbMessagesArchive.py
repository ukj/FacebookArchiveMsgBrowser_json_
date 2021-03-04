import json
import re
import os
from datetime import datetime
import zipfile
from zipfile import ZipFile  # Kipub ise avatud zip faili sulgema
# või kas tekib klassi objektist koopia millel fail on avamata?
# seeparast iga meetod avab faili ikkagi uuesti
# faili lugemine  with käsuga sulgeb ise

#from ukj_ee.yt_basicMeta import yt_basicMeta
from ukj_ee.FbMsgFiltrid import *


# def myLogger(line, msg):
#     with open("my-logger.txt", "a") as myfile:
#         myfile.write("%s\t%s\t%s\n" %
#                      (datetime.timestamp(datetime.now()), line, msg))

class FbMessagesArchive:
    '''Loeb Facebooki arhiivist vestlusi ja manuseid; ukj@ukj.ee, 2021'''

    Zip_f = ''  # failitee
    Zip_fp = None  # faili osuti
    
    MsgBoxes = []
    this_MsgBox = ''
    Conversation = {}
    Metainfo =  {'msg_box':'', 'conv_id': '', 'host': '','title':'', 'participants': []}

    yt_cache_path = ''
    yt_api_key = ''

    #def __init__(self):

    def get_urls(self, text):
        '''
        Eraldab sõnumi tekstist urlid

        Parameters
        ----------
        text : str, mis sisaldab urle
        Returns list
        '''
        links_tmp = re.findall(
            r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text)
        return links_tmp

    def get_emails(self, text):
        '''Eraldab e-maili aadressid
        * https://www.tutorialspoint.com/Extracting-email-addresses-using-regular-expressions-in-Python
        '''
        emails_tmp = re.findall(r"([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)", text)
        return emails_tmp

    def get_numbers(self, text):
        '''Eraldab numbrid'''
        nums = re.findall(r"([()\-+\d]{3,6}[.,%$€¥¢~*+/#+\- \d]{1,})", text)
        i = 0
        for n in nums:
            nums[i] = n.strip()
            i += 1
        return nums

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
                fbstr[key] = list(map(lambda x: x if type(x) != str else x.encode(
                    'latin_1').decode('utf-8'), fbstr[key]))
            # pass
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
            self.MsgBoxes = []
            for f in ZipFile(FbArchiveZip, 'r').namelist():
                if f.startswith('messages/inbox/'):
                    self.Zip_f = FbArchiveZip
                    return True
        return False

    def is_loaded(self):
        '''Kas fail on teada?'''
        if self.Zip_f != '':
            return True
        else:
            return False

    # def set_yt_api_key(self, key):
    #     self.yt_api_key=key

    def set_yt_cache_path(self, path):
        self.yt_cache_path = path

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
        self.MsgBoxes = threads
        return threads

    def get_conversations(self, box='inbox'):
        '''
        Vestluste nimekiri

        Parameters
        ----------
        FbArchiveZip : str, inbox, archieved_threads
        Returns
        -------
        dict, nimed/id, {'idnimi':'fullid'}

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
        self.this_MsgBox = box
        return conv

    
    def get_conv_meta_participiants(self):
        ''' vastluskaaslased 
        returns:list vestluskaaslased'''
        return self.Metainfo['participants']
    
    def get_conv_meta_title(self):
        ''' vestluse pealkiri'''
        return self.Metainfo['title']
    
    def load_conversation(self, conv_id, own_name):
        '''
        Võtab ühe vestluse ja eraldab tekstist lingid/e-mailid/numbrid ja laiendab manuste jaotist

        Vestluse osaliste nimede võtmine, mitme json läbimine
        * https://masterscrat.github.io/Chatistics/ (MIT License)
        * https://thispointer.com/python-how-to-get-the-list-of-all-files-in-a-zip-archive/
        * https://thispointer.com/python-how-to-unzip-a-file-extract-single-multiple-or-all-files-from-a-zip-archive/

        Parameters
        ----------
        FacebookArchiveZip : str, failitee
        conversation_id : str, box/vestlus
        own_name : str, Enda nimi
        Returns
        -------
        list, [vestlus [int_timestamp_ms, str_sender_name, str_content, [attachments {type:content}, {type:content, title:title, thumbnail:uri}] ]]
        '''
        # print('load_conversation() ', conv_id)
        self.Metainfo = {'msg_box':'', 'conv_id': '', 'host': '','title':'', 'participants': []}
        self.Conversation = {}
        ci = 0 # sõnumite loendur
        conversation_with_name = None
        self.Zip_fp = ZipFile(self.Zip_f, 'r')
        with self.Zip_fp as zipObj:
            listOfiles = zipObj.namelist()
            for fileName in listOfiles:
                if fileName.endswith(".json") and fileName.startswith(f"messages/{self.this_MsgBox}/{conv_id}/message_"):
                    a_file = zipObj.read(fileName)
                    json_data = json.loads(
                        a_file, object_hook=self.fb_reEncode)
                    # TODO: Mitme vestluskaaslase käsitlemine ja sõnumite lugemine kui kaaslaste nimekiri puuduks aga vestlus siiski on, kas saab nii olla?
                    if "messages" not in json_data or "participants" not in json_data:
                        continue

                    participants = json_data["participants"]
                    conv_title = json_data["title"]
                    for participant in participants:
                        if participant['name'] != own_name:
                            conversation_with_name = participant['name']
                        if conversation_with_name is None:
                            conversation_with_name = conv_title
                        
                        # Et mitme faili pärast ei tekiks kordusi
                        if conversation_with_name not in self.Metainfo['participants']:
                            self.Metainfo['participants'].append(conversation_with_name)
                    
                    self.Metainfo['conv_id'] = conv_id
                    self.Metainfo['host'] = own_name
                    self.Metainfo['title'] = conv_title

                    for message in json_data["messages"]:
                        #print('load msg')
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
                                content_tmp = message['content']
                                for file in self.get_urls(content_tmp):
                                    file = file.strip()
                                    if file != '':
                                        content_tmp = content_tmp.replace(
                                            file, '')
                                        attachments.append({'link': file})

                                for file in self.get_emails(content_tmp):
                                    file = file.strip()
                                    if file != '':
                                        content_tmp = content_tmp.replace(
                                            file, '')
                                        attachments.append({'email': file})
                                        #print('email: ', file)

                                for file in self.get_numbers(content_tmp):
                                    file = file.strip()
                                    if file != '':
                                        attachments.append({'number': file})
                                        #print('number: ', file)

                            if 'photos' in message:
                                for file in message['photos']:
                                    attachments.append({'photo': file['uri']})
                                    # attachments['photo']=file['uri']

                            if 'sticker' in message:
                                attachments.append(
                                    {'sticker': message['sticker']['uri']})

                            if 'audio_files' in message:
                                for file in message['audio_files']:
                                    attachments.append({'audio': file['uri']})
                                    # attachments['audio']=file['uri']

                            if 'videos' in message:
                                for file in message['videos']:
                                    attachments.append(
                                        {'video': file['uri'], 'thumbnail': file['thumbnail']['uri']})

                            if 'files' in message:
                                for file in message['files']:
                                    attachments.append({'file': file['uri']})

                            if 'Share' in message:
                                attachments.append(
                                    {'link': message['share']['link']})

                            self.Conversation[ci] = [
                                timestamp_ms, sender_name, content, attachments]
                            ci += 1
                            # if len(data) >= MAX_EXPORTED_MESSAGES:
                            #log.warning(f'Reached max exported messages limit of {MAX_EXPORTED_MESSAGES}. Increase limit in order to parse all messages.')
                            # return data
        self.init_filters()
    
    
    
    
    
    
    
    
    
    # Saadaolevate filtrite nimed ja funktsioonid
    # TODO: Selle peaks täitma get_filter_names() või eraldi laadur
    conversation_filters = {'FbMsgF_GenFilteringType': ['general_filtering_type'],
                            'FbMsgF_FindText': ['content','message_time','sender_name'],
                            'FbMsgF_YouTubeTitles': ['attachments'],
                            'FbMsgF_to_CSV':['get_csv'] }
    # loodud filtrite objektid
    conversation_filters_active = {}
    Conversation_Filtered = {}

    def get_filter_names(self):
        ''' TODO: Tulevikus peab kasutama getattr või importlib'''
        #self.conversation_filters_selected = [n for n in names if n in self.conversation_filters]       
        return self.conversation_filters.keys()

    def init_filters(self):
        ''' iga init peab tegema filtri/plugina tüübile lubatud andmete
        jagamised'''
        for n in self.conversation_filters.keys():
            # print('init_filters() init ', n)
            if n == 'FbMsgF_YouTubeTitles':
                self.conversation_filters_active[n] = FbMsgF_YouTubeTitles(cache=self.yt_cache_path)
            elif n == 'FbMsgF_FindText':
                self.conversation_filters_active[n] = FbMsgF_FindText()
                for ftype in self.conversation_filters[n]:
                    if ftype == 'sender_name':
                        # TODO: Seda võin olla parem teha pärimisega
                        #       enne peab tegema eraldi korraliku pärimise mudeli ja selle järgi kogu asja uuesti
                        self.conversation_filters_active[n].set_participants(self.Metainfo['participants'] )
                
            elif n == 'FbMsgF_GenFilteringType':
                self.conversation_filters_active[n] = FbMsgF_GenFilteringType()
            elif n == 'FbMsgF_to_CSV':
                self.conversation_filters_active[n] = FbMsgF_to_CSV()
                 
    def get_filter_display(self, name, parent):
        return self.conversation_filters_active[name].display(parent)


    
    
    
    
    def conversation_filtering(self):
        '''
        * https://realpython.com/iterate-through-dictionary-python/
        '''
        if len(self.conversation_filters_active) == 0:
            return self.Conversation

        # print( 'FbMsgF_YouTubeTitles.is_set()', self.conversation_filters_active['FbMsgF_YouTubeTitles'].is_set() )
        self.Conversation_Filtered = {}
        # {vestlus 0:[0int_timestamp_ms, 1str_sender_name, 2str_content,
        #       3[attachments {type:content},
        #                    {type:content/uri/url, title:title, thumbnail:uri}]
        #       ]
        # }
        for i in range(len(self.Conversation)):
            results=[]
            
            
            Saatja = self.Conversation[i][1]
            for fn, fo in self.conversation_filters_active.items():
                if 'sender_name' in self.conversation_filters[fn]:
                    results.append(fo.sender_name(Saatja))           
            
            
            Aeg = datetime.utcfromtimestamp(
                int(self.Conversation[i][0]/1000)).strftime('%Y-%m-%d %H:%M:%S')
            for fn, fo in self.conversation_filters_active.items():
                if 'message_time' in self.conversation_filters[fn]:
                    results.append(fo.message_time(Aeg))  
            
            Sonum = self.Conversation[i][2]
            for fn, fo in self.conversation_filters_active.items():
                if 'content' in self.conversation_filters[fn]:
                    results.append(fo.content(Sonum))
            
            # Igale manuse filtrile antakse näha selle sõnumi manust
            # Sõnum/manus valitakse siis kui ükski filter tagastab
            Manused = self.Conversation[i][3]
            if len(Manused) > 0:
                for fn, fo in self.conversation_filters_active.items():
                    if 'attachments' in self.conversation_filters[fn]:
                        Manused_status, Manused = fo.attachments(Manused)
                        results.append(Manused_status)
                        #if Manused_status is True:
                        #    Manused = result

        
            # Plugin kas mõni või kõik  filtritest peavad läbima any() | all()
            for fn, fo in self.conversation_filters_active.items():
                if 'general_filtering_type' in self.conversation_filters[fn]:
                    if fo.general_filtering_type(results):
                        #self.Conversation_Filtered.append([Aeg, Saatja, Sonum, Manused]) #[]
                        self.Conversation_Filtered[i] = [Aeg, Saatja, Sonum, Manused] #{}


    def get_conversation_CSV(self):
        # print('get_conversation_CSV()')
        return self.conversation_filters_active['FbMsgF_to_CSV'].get_csv(self.Conversation_Filtered)
        
