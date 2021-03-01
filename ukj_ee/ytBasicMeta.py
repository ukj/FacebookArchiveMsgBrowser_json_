import re, json, urllib
from datetime import datetime
import calendar
from urllib.request import Request, urlopen
#from urllib.error import URLError, HTTPError
import sqlite3 #youtube meta

class ytBasicMeta:
    """Youtube video teave; ukj@ukj.ee,2021"""
    
    yt_API_key=''
    cache_path=''
    cache_dbconn=None
    cache_cursor=None
        
    def __init__(self, key=None, cache=''):
        '''
        Alustamine
        
        * https://www.sqlitetutorial.net/sqlite-python/
        
        Parameters
        ----------
        key : str, Optional API key
        '''
        if key != None:
            self.set_api_key(key)
            self.set_cache_file(cache)
            self.cache_dbconn = sqlite3.connect(self.cache_path) 
            self.cache_cursor = self.cache_dbconn.cursor()
            self.cache_exists('yt_movies')
            print(f"yt init cache path {cache}")
            
    def get_shortUrl(self, url):
        '''Lühike link'''
        vid = self.get_idFromUrl(url)
        if isinstance(vid, str) and vid != '':
            return 'https://youtu.be/'+vid
        else:
            return vid
    
    def set_api_key(self, key):
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



           
    def set_cache_file(self, path=''):
        '''kus hoida vahemälu'''
        if path=='':
           path = 'yt_basicMeta.sqlite'
        self.cache_path=path


    def get_meta_from_url(self, url):
        '''
        Video teave urli järgi
        
        Parameters
        ----------
        url : str, Video URL
        
        Returns
        -------
        dict, {title, author, pubdate, description, thumbnail(url)}
        '''
        vid = self.get_idFromUrl(url)
        return self.yt_meta(vid)
    
    def get_meta_from_vid(self, vid):
        '''
        Video teave video id järgi
        
        Parameters
        ----------
        vid : str, Video id
        
        Returns
        -------
        dict, {title, author, pubdate, description, thumbnail(url)}
        '''
        return self.yt_meta(vid)





        
    def get_idFromUrl(self, yt_url):
        '''
        Extracts video id from url
        
        https://stackoverflow.com/questions/34833232/get-youtube-video-id-from-url-with-python-and-regex
        
        Parameters
        ----------
        yt_url : str
        
        Returns
        -------
        str
        '''    
        pattern = r'(?:https?:\/\/)?(?:[0-9A-Z-]+\.)?(?:youtube|youtu|youtube-nocookie)\.(?:com|be)\/(?:watch\?v=|watch\?.+&v=|embed\/|v\/|.+\?v=)?([^&=\n%\?]{11})'
        yt_ids = re.findall(pattern, yt_url, re.MULTILINE | re.IGNORECASE)
        if len(yt_ids)>0:
            return yt_ids[0]
        else:
            return ''
    
       
    def yt_meta(self, vid):
        '''
        Downloads and parses video metadata
        
        https://developers.google.com/youtube/v3/getting-started
        
        Parameters
        ----------
        vid : str, video id
        
        Returns
        -------
        dict, {title, author, pubdate, description, thumbnail(url), reslen(response len)}
        '''
        y_json=title=author=date=desc=thumb=''
        if vid != '' and self.yt_API_key!='':
            
            is_cached=self.in_cache(vid)
            if isinstance(is_cached, dict):
                return is_cached 
            
            #else:
            youtube_url = 'https://www.googleapis.com/youtube/v3/videos?id='+vid+'&key='+self.yt_API_key+'&part=snippet&fields=items(snippet)'
            y_req  = urllib.request.Request(youtube_url)
            y_res  = urllib.request.urlopen(y_req) 
            y_json = y_res.read().decode('utf8')
            json_data = json.loads(y_json)
            if "items" in json_data and len(json_data['items'])>0:
                #print(ytvid,': ',json_data)
                title  = json_data['items'][0]['snippet']['title']
                author = json_data['items'][0]['snippet']['channelTitle']
                date  = json_data['items'][0]['snippet']['publishedAt']
                desc  = json_data['items'][0]['snippet']['description']
                thumb = json_data['items'][0]['snippet']['thumbnails']['default']['url']
            else:
                desc='[Ei õnnestunud teavet hankida!]'
            
            #caching
            if is_cached is False:
                self.to_cache(vid, title, author, desc, date, thumb)
                
                return {'title':title, 'description':desc, 'author':author, 'pubdate':date,  'thumbnail':thumb, 'reslen':len(y_json) }






    def ISO8601ToEpoch(self,theString):
        '''Aja teisendamine

        * https://www.devdungeon.com/content/working-dates-and-times-python-3
        * https://docs.python.org/3/library/datetime.html#datetime.datetime.timestamp
        
        Parameters
        ----------
        theString: str, iso kuupäev
        Returns
        -------
        float
        '''
        return datetime.strptime(theString, '%Y-%m-%dT%H:%M:%S.%fZ%z').timestamp()
        
    def EpochToISO8601(self,theEpoch):
        '''Aja teisendamine

        Returns
        -------
        str
        '''
        return datetime.fromtimestamp(theEpoch).isoformat()



    def cache_exists(self, table_name='yt_movies'):
        '''Kas vahemälu hoidla on olemas'''
        self.cache_cursor.execute('''SELECT count(name) FROM sqlite_master WHERE TYPE = 'table' AND name = '{}' '''.format(table_name)) 
        if self.cache_cursor.fetchone()[0] == 1: 
            return True 
        else:
            self.cache_cursor.execute(f'''CREATE TABLE {table_name}(
                vid TEXT, 
                title TEXT, 
                author TEXT,
                publishedAt TEXT,
                description TEXT,
                thumbnail TEXT)''')
            self.cache_dbconn.commit()
                        
    def to_cache(self, vid, title, author, desc, pubdate, thumb):
        '''Vahemällu panemine

        Parameters
        ----------
        vid: str, video id
        title:str, pealkiri
        author:str, autor, kanal
        desc:str, kirjeldus
        pubdate:str|int
        thumb:str, url
        
        * https://towardsdatascience.com/python-has-a-built-in-database-heres-how-to-use-it-47826c10648a
        '''
        self.cache_cursor.execute(''' INSERT INTO yt_movies (vid, title, author,  publishedAt, description, thumbnail) VALUES(?, ?, ?, ?, ?, ?) ''', (vid, title, author, pubdate, desc, thumb)) 
        self.cache_dbconn.commit()        

    def in_cache(self, vid):
        """Kas vahemälu on loodud"""
        # SELECT datetime(1319017136629, 'unixepoch', 'localtime');
        self.cache_cursor.execute('''SELECT * FROM yt_movies WHERE vid = "{}"'''.format(vid)) 
        data = []
        for row in self.cache_cursor.fetchall():  
            data.append(row) 
        
        if len(data) > 0:
            return {'title':data[0][1], 'description':data[0][4], 'author':data[0][2], 'pubdate':data[0][3],  'thumbnail':data[0][5], 'reslen':0 }
        else:
            return False







'''
if __name__ == "__main__":
    yt = yt_basicMeta('AIzaSyC-rkBNmZ8kpH6N0Qfg-u1sDF3zdboMlZo')
    yt.set_cache_file('yt_basicMeta.sqlite')
    
    long='https://www.youtube.com/watch?v=RamJDpZQbr4&t=128s'
    short='https://youtu.be/DRYzImN_bDM'
    vid='R1Sy9RatBs0'
    
    yt_short = yt.get_shortUrl(long)
    yt_meta_url = yt.get_meta_from_url(short)
    yt_meta_vid = yt.get_meta_from_vid(vid)
    
    print(long,' > ', yt_short)
    print(short,' > ',yt_meta_url)
    print(vid,' > ',yt_meta_vid)

'''
# * https://www.askpython.com/python/examples/find-all-methods-of-class
# * https://blog.teamtreehouse.com/python-single-line-loops

#for method in [method for method in dir(yt_basicMeta) if method.startswith('_') is False]:
#    exec(f"print(yt_basicMeta.{method}.__doc__)")
