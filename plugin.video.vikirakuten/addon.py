# -*- coding: utf-8 -*-

"""
    VIKI Rakuten® addon Add-on
"""

import re
import sys
import os
import time
import json
from urllib.parse import parse_qsl, quote_plus, urlparse, urlunparse, parse_qs, urlencode
import urllib.request, urllib.error
from urllib.error import URLError, HTTPError
from resources.libs import lang_sel
import requests
from hashlib import sha1
import hmac
import binascii
import base64
import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon
import xbmcvfs
import inputstreamhelper
import YDStreamExtractor

from resources.libs import common

#sys.path.append("C:\Program Files\JetBrains\PyCharm 2019.2.6\debug-eggs\pydevd-pycharm.egg")
#import pydevd_pycharm
#pydevd_pycharm.settrace('localhost', port=5678, stdoutToServer=True, stderrToServer=True)

__settings__ = lang_sel.getSetting
my_addon = common.my_addon
my_addon_id = common.my_addon_id
ADDON_PATH = common.ADDON_PATH
DATA_PATH = common.DATA_PATH
MEDIA_PATH = common.MEDIA_PATH
searchFile = common.searchFile
md = MEDIA_PATH
MUA = 'Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/ 604.1.21 (KHTML, like Gecko) Version/ 12.0 Mobile/17A6278a Safari/602.1.26'
UA = 'Mozilla/5.0 (Macintosh; MacOS X10_14_3; rv;93.0) Gecko/20100101 Firefox/93.0'
header = {'user-agent': UA}
headmobile = {'user-agent': MUA}
SEARCH_URL = 'https://api.viki.io/v4/search.json?page=1&per_page=50&app=100000a&term='
system_lang = xbmc.getLanguage()
params = dict(parse_qsl(sys.argv[2].replace("?", "")))

#Dostosuj jakość wideo
quality =__settings__('quality')

#Wsparcie dla kanału fanów
fc =__settings__('fc')

#Tryb debugowania
debug =__settings__('debug')

#Ustaw kolejność odcinków
d =__settings__('direction')
if d == '0': order = '&direction=desc'
elif d == '1': order = '&direction=asc'

#Ustaw język napisów
se = __settings__('se')
lang = lang_sel.lang
language = lang_sel.language


#Menu z katalogami we wtyczce
def CATEGORIES():
    addDir('Search','','','search',md+'DefaultAddonsSearch.png') #Search32010
    addLink('Play video by ID','loadbyid','0','True','','','G','5.0','loadID',md+'DefaultStudios.png')
    addDir('Browse Movies by Genre','movies','','genre',md+'DefaultFolder.png')
    addDir('Browse Movies by Country','movies','','country',md+'DefaultFolder.png')
    addDir('New Movies','https://api.viki.io/v4/movies.json?sort=newest_video&page=1&per_page=50&app=100000a&t=','','index',md+'DefaultFolder.png')
    addDir('Recent Movies','https://api.viki.io/v4/movies.json?sort=views_recent&page=1&per_page=50&app=100000a&t=','','index',md+'DefaultFolder.png')
    addDir('Popular Movies','https://api.viki.io/v4/movies.json?sort=trending&page=1&per_page=50&app=100000a&t=','','index',md+'DefaultFolder.png')
    addDir('Best Movies','https://api.viki.io/v4/movies.json?sort=views&page=1&per_page=50&app=100000a&t=','','index',md+'DefaultFolder.png')
    addDir('Browse Series by Genre','series','','genre',md+'DefaultFolder.png')
    addDir('Browse Series by Country','series','','country',md+'DefaultFolder.png')
    addDir('New Series','https://api.viki.io/v4/series.json?sort=newest_video&page=1&per_page=50&app=100000a&t=','','index',md+'DefaultFolder.png')
    addDir('Recent Series','https://api.viki.io/v4/series.json?sort=views_recent&page=1&per_page=50&app=100000a&t=','','index',md+'DefaultFolder.png')
    addDir('Popular Series','https://api.viki.io/v4/series.json?sort=trending&page=1&per_page=50&app=100000a&t=','','index',md+'DefaultFolder.png')
    addDir('Best Series','https://api.viki.io/v4/series.json?sort=views&page=1&per_page=50&app=100000a&t=','','index',md+'DefaultFolder.png')
    addDir('Latest Clips','https://api.viki.io/v4/clips.json?sort=newest_video&page=1&per_page=50&app=100000a&t=','','index',md+'DefaultFolder.png')

#Przewiń tytuły przesłanej strony
def INDEX(url):

    ################
    timestamp = str(int(time.time()))

    try:
        if 'search.json' in url:
            jsonrsp = requests.get(url, headers=header, timeout=5).json()
        else:
            jsonrsp = requests.get(url+timestamp, headers=header, timeout=5).json()

        print (jsonrsp['response'][0]['titles']['en'])

    #Rozpocznij indeksowanie
        for movie in range(0, len(jsonrsp['response'])):

                if (jsonrsp['response'][movie]['flags']['licensed'] == True or fc == 'true' or debug == 'true'): #Ако заглавието е лицензирано или са разрешени Фен каналите/дебъг режима
                    if jsonrsp['response'][movie]['type'] == 'series': #Jeśli to seria
                        try: #Tytuł w języku angielskim
                            mt = str(jsonrsp['response'][movie]['titles']['en']).encode('utf-8', 'ignore')
                        except:
                            mt = 'TV Show Title'
                        try: #Opis w języku angielskim
                            mdes = str(jsonrsp['response'][movie]['descriptions']['en']).encode('utf-8', 'ignore')
                        except:
                            mdes = ''
                        try: #Poster
                            pos = jsonrsp['response'][movie]['images']['poster']['url']
                        except:
                            pos = ''
                        xbmcplugin.setContent(int(sys.argv[1]), 'season')
                        addDir(mt,'https://api.viki.io/v4/series/'+jsonrsp['response'][movie]['id']+'/episodes.json?page=1&per_page=50&app=100000a&t='+timestamp,mdes,'prepare',pos)

                    else: #Jeśli jest to film fabularny lub wideo
                        if (jsonrsp['response'][movie]['blocked'] == False or debug == 'true'): #Проверка за достъпност
                            try: #Napisy lokalne
                                subs_local = str(jsonrsp['response'][movie]['subtitle_completions'][lang], 'utf-8', 'ignore')
                            except:
                                subs_local = '0'
                            try: #angielskie napisy
                                subs_en = str(jsonrsp['response'][movie]['subtitle_completions']['en'], 'utf-8', 'ignore')
                            except:
                                subs_en = '0'
                            try: #Czas trwania filmu
                                dur = str(jsonrsp['response'][movie]['duration'])
                            except:
                                dur = ''
                            try: #Rozdzielczość wideo
                                hd = str(jsonrsp['response'][movie]['flags']['hd'])
                            except:
                                hd = 'False'
                            try: #Nazwa / opis filmu
                                mt = str(jsonrsp['response'][movie]['titles']['en'])
                            except:
                                mt = 'Movie Title'
                            try: #Autor / Studio
                                at = str(jsonrsp['response'][movie]['author'], 'utf-8', 'ignore')
                            except:
                                at = ''
                            try: #Movie ID
                                mid = str(jsonrsp['response'][movie]['id'])
                            except:
                                mid = ''
                            try: #Poster
                                pos = str(jsonrsp['response'][movie]['images']['poster']['url'])
                            except:
                                pos = ''
                            try: #Ocena
                                rating = jsonrsp['response'][movie]['rating']
                            except:
                                rating = 'G'
                            try: #Stopień
                                ar = str(jsonrsp['response'][movie]['container']['review_stats']['average_rating'])
                            except:
                                ar = '0'
                            xbmcplugin.setContent(int(sys.argv[1]), 'movie')
                            addLink(mt,mid+'@'+pos+'@'+subs_local+'@'+subs_en+'@'+mt,dur,hd,mt,at,rating,ar,'play',pos)
        #######################

    except:
        pass
        #xbmc.executebuiltin('Notification(%s, %s, %d, %s)'%('VIKI®','Error in INDEX Function', 4000, md+'DefaultIconError.png'))
    #Koniec indeksowania

    #next page...
    if jsonrsp['more'] == True:

        fronturl, page, backurl = re.findall('(.+?)&page=(.+?)&per_page=(.+?)&t=', url)[0]
        newpage = int(page) + 1
        url = fronturl + '&page=' + str(newpage) + '&per_page=' + backurl + '&t='
        addDir('Next page >>', url, '', 'index', md + 'DefaultFolder.png')

#Przeglądanie odcinków serialu
def PREPARE(url):

    xbmcplugin.setContent(int(sys.argv[1]), 'episode')
    timestamp = str(int(time.time()))
    jsonrsp = requests.get(url + order, headers=header).json()

    #print (jsonrsp)

    #Rozpocznij indeksowanie
    for episode in range(0, len(jsonrsp['response'])):
        try:
            if (jsonrsp['response'][episode]['blocked'] == False or debug == 'true'): #Kontrola dostępności — zablokowana lub nie
                try: #Nazwa serii
                    tsn = str(jsonrsp['response'][episode]['container']['titles']['en'])
                except:
                    tsn = ''
                try: #Numer odcinka serialu
                    ep = ' Episode ' + str(jsonrsp['response'][episode]['number'])
                except:
                    ep = ''
                try: #Identyfikator odcinka
                    video_id = str(jsonrsp['response'][episode]['id'])
                except:
                    video_id = ''
                try: #Poster URL
                    pos = str(jsonrsp['response'][episode]['images']['poster']['url'])
                except:
                    pos = ''
                try: #Duration
                    dur = str(jsonrsp['response'][episode]['duration'])
                except:
                    dur = ''
                try: #Średnia ocena
                    ar = str(jsonrsp['response'][episode]['container']['review_stats']['average_rating'])
                except:
                    ar = ''
                try: #Napisy lokalne
                    subs_local = str(jsonrsp['response'][episode]['subtitle_completions'][lang])
                except:
                    subs_local = '0'
                try: #angielskie napisy
                    subs_en = str(jsonrsp['response'][episode]['subtitle_completions']['en'])
                except:
                    subs_en = '0'
                try: #Rozdzielczość wideo
                    hd = str(jsonrsp['response'][episode]['flags']['hd'])
                except:
                    hd = 'False'
                try: #Nazwa / opis odcinka
                    et = str(jsonrsp['response'][episode]['titles'][lang])
                except:
                    et = ''
                try: #Autor / Studio
                    at = str(jsonrsp['response'][episode]['author'])
                except:
                    at = ''
                try: #Ocena
                    rating = str(jsonrsp['response'][episode]['rating'])
                except:
                    rating = 'G'

                addLink(tsn + ep, video_id +'@'+pos+'@'+subs_local+'@'+subs_en+'@'+et,dur,hd,et,at,rating,ar,'play',pos)

        except:
            xbmc.executebuiltin('Notification(%s, %s, %d, %s)'%('VIKI®','Error in PREPARE Function', 4000, md+'DefaultIconError.png'))
    if len(jsonrsp['response'])==0:
        addDir('There are no episodes for now','','','',md+'DefaultFolderBack.png')
    #Koniec indeksowania

    #Jeśli mamy więcej stron...
    if jsonrsp['more'] == True:
        getpage=re.compile('(.+?)page=(.+?)&per_page').findall(url)
        for fronturl,page in getpage:
            newpage = int(page)+1
            url = fronturl + 'page=' + str(newpage) + '&per_page=50&app=100000a&t=' + timestamp
            #print 'URL OF THE NEXT PAGE IS' + url
            addDir('Next page >>',url,'','prepare',md+'DefaultFolder.png')

#Gatunki
def GENRE(url):

    xbmcplugin.setContent(int(sys.argv[1]), 'season')
    link = 'https://api.viki.io/v4/videos/genres.json?app=100000a'
    jsonrsp = requests.get(link + order, headers=header).json()

    #print jsonrsp[0]['name']['en']

    for genre in range(0, len(jsonrsp)):
        addDir(jsonrsp[genre]['name']['en'],'https://api.viki.io/v4/'+url+'.json?sort=newest_video&page=1&per_page=50&app=100000a&genre='+jsonrsp[genre]['id']+'&t=','','index',md+'DefaultFolder.png')


#Kraj
def COUNTRY(url):
    xbmcplugin.setContent(int(sys.argv[1]), 'season')
    link = 'https://api.viki.io/v4/videos/countries.json?app=100000a'

    jsonrsp = requests.get(link + order, headers=header).json()
    #print jsonrsp['ae']['name']['en']

    for country, subdict in jsonrsp.items():
        addDir(jsonrsp[country]['name']['en'],'https://api.viki.io/v4/'+url+'.json?sort=newest_video&page=1&per_page=50&app=100000a&origin_country='+country+'&t=','','index',md+'DefaultFolder.png')

def SEARCH():

    addDir("New search...",'','',"movieSearchnew", md+'DefaultAddonsSearch.png')#"New search..."32603

    from sqlite3 import dbapi2 as database

    dbcon = database.connect(searchFile)
    dbcur = dbcon.cursor()

    try:
        dbcur.executescript(
            "CREATE TABLE IF NOT EXISTS movies (ID Integer PRIMARY KEY AUTOINCREMENT, term);"
        )
    except:
        pass

    dbcur.execute("SELECT * FROM movies ORDER BY ID DESC")
    lst = []

    delete_option = False
    for (id, term) in dbcur.fetchall():
        if term not in str(lst):
            delete_option = True
            addDir(term, "","", "movieSearchterm&name=%s" % term, md+'DefaultAddonsSearch.png')
            lst += [(term)]
    dbcur.close()

    if delete_option:
        addDir("Click to clear search history",'','', "clearCacheSearch", md+'DefaultAddonsSearch.png') #"Naciśnij aby wyczyścić historię"#32605


def search_new(url):
#	control.idle()
#	t = control.lang(32010).encode("utf-8")
#	k = control.keyboard("", t)
    xbmcplugin.setContent(int(sys.argv[1]), 'season')
    k = xbmc.Keyboard('', 'Search in VIKI® Database')
    k.doModal()
    q = k.getText() if k.isConfirmed() else None
    if q == None or q == "":
        addDir('Go to main menu...','','','',md+'DefaultFolderBack.png')
#	q = cleantitle.normalize(q)  # for polish characters
#	control.busy()

    from sqlite3 import dbapi2 as database

    dbcon = database.connect(searchFile)
    dbcur = dbcon.cursor()
    dbcur.execute("INSERT INTO movies VALUES (?,?)", (None, q))
    dbcon.commit()
    dbcur.close()

    q = quote_plus(name)
    #print ('SEARCHING:' + q)
    INDEX(url + q)


def search_term(url, name):

    INDEX(url + quote_plus(name))

#Załaduj klip według ID
def LOADBYID():
        keyb = xbmc.Keyboard('', 'Enter video ID ...videos/xxxxxxv only')
        keyb.doModal()
        if (keyb.isConfirmed()):
            vid = quote_plus(keyb.getText())
            #print 'LOADBYID:' + vid
            PLAY('VIKI®',vid+'@0@50',md+'DefaultStudios.png')
        else:
            addDir('Go to main menu...','','','',md+'DefaultFolderBack.png')


#Podpisywanie wniosków w imieniu Flash Playera
def SIGN(url,pth):

    timestamp = str(int(time.time()))
    key = 'd96704b180208dbb2efa30fe44c48bd8690441af9f567ba8fd710a72badc85198f7472'
    rawtxt = '/v4/videos/'+url+pth+'?app=100005a&t='+timestamp+'&site=www.viki.com'
    hashed = hmac.new(key.encode('utf-8'), rawtxt.encode('utf-8'), sha1)
    signatura = binascii.hexlify(hashed.digest())
    fullurl = 'https://api.viki.io' + rawtxt+'&sig='+signatura.decode('utf-8')
    #print ('fullurl:'+fullurl)
    return fullurl

#Prześlij filmy i napisy

def PLAY(name,url,iconimage):

        url, thumbnail, subtitle_completion1, subtitle_completion2, plot = url.split("@")
        #url, thumbnail, subtitle_completion1, subtitle_completion2 = url.split("@")

        #Prośba o napisy
        try:
            if (int(subtitle_completion1)>79 and se=='true'): #Jeśli przetłumaczone ponad 79% napisów w naszym języku
                srtsubs_path = xbmcvfs.translatePath('special://temp/vikirakuten.'+language+'.srt')

                #xbmc.executebuiltin('Notification(%s, %s, %d, %s)'%('VIKI®',language+' subtitles at '+subtitle_completion1+'%', 4000, md+'DefaultAddonSubtitles.png'))

                urllib.request.urlcleanup()
                urllib.request.urlretrieve(SIGN(url,'/subtitles/'+lang+'.srt'), srtsubs_path)

                sub = 'true'
            elif (int(subtitle_completion2)>0 and se=='true'): #Przełączamy się na napisy w języku angielskim
                srtsubs_path = common.srtsubs_path
                #xbmc.executebuiltin('Notification(%s, %s, %d, %s)'%('VIKI®','English subtitles at '+subtitle_completion2+'%', 4000, md+'DefaultAddonSubtitles.png'))
                urllib.request.urlcleanup()
                urllib.request.urlretrieve(SIGN(url,'/subtitles/en.srt'), srtsubs_path)

                sub = 'true'
            else:
                sub = 'false' #Jeśli nie są dostępne napisy
                xbmc.executebuiltin('Notification(%s, %s, %d, %s)'%('VIKI®','Subtitles not available or disabled', 4000, md+'DefaultAddonSubtitles.png'))
        except:
            sub = 'false' #Jeśli wystąpił błąd w odbiorze napisów
            xbmc.executebuiltin('Notification(%s, %s, %d, %s)'%('VIKI®','Error in providing Subtitles', 4000, md+'DefaultIconError.png'))

        rapi = 'true'
        #Prośba o otrzymanie strumienia wideo z API
        if (debug == 'false' and rapi == 'true'):
            try:
                viki_headers = {
                'User-Agent': UA,
                'authority': 'manifest-viki.viki.io',
                'accept': '*/*',
                'x-client-user-agent': UA,
                'X-Viki-manufacturer': 'vivo',
                'X-Viki-device-model': 'vivo 1606',
                'X-Viki-device-os-ver': '6.0.1',
                'X-Viki-connection-type': 'WIFI',
                'X-Viki-carrier': '',
                'X-Viki-as-id': '100005a-1625321982-3932',
                'x-viki-app-ver': '6.0.0',
                'dnt': '1',
                'origin': 'https://www.viki.com',
                'referer': 'https://www.viki.com',
                'Connection': 'keep-alive',
                'sec-fetch-site': 'cross-site',
                'sec-fetch-mode': 'cors',
                'sec-fetch-dest': 'empty',
                'referer': url,
                'accept-language': 'en;q=0.8',
                'Accept-Encoding': 'gzip'
                                    }

                web = 'https://www.viki.com/videos/' + url + '-viki-link'
                #Podpisanie wniosku
                #print (SIGN(url,'/streams.json'))
                #response = requests.get(SIGN(url,'/streams.json'), headers=viki_headers)
                #jsonrsp = response.json()
                #jsonrsp = ''
                #print (SIGN(url,'/streams.json'))
                #print (jsonrsp['mpd']['http']['url'])
                #print (jsonrsp)

                #print (url)

                vid = YDStreamExtractor.getVideoInfo(web,quality=2) #quality is 0=SD, 1=720p, 2=1080p and is a maximum
                test = vid._streams[0]['ytdl_format']['requested_formats'][0]
                #test2 = vid.ID
                stream1 = test['manifest_url']
                stream = vid.streamURL()
                manifest = requests.get(test['manifest_url']).text
                #print('dupa')
#                test2 = test.json()


#                stream = vid.streamURL() #This is what Kodi (XBMC) will play

            #Jakość wybrana przez użytkownika
                    #if 'mpd' in jsonrsp:
                    #if (quality == '3' or quality == '2'): #MPEG-DASH DYNAMIC MOBILE
                #stream = jsonrsp['mpd']['http']['url'] #.replace('https','http')
                #xbmc.executebuiltin("Notification(VIKI®,Dynamic Streaming: MPEG-DASH,2000)")
                #elif quality == '2': #MPEG-DASH 480p
                    #stream = jsonrsp['480p']['https']['url'].replace('https','http').replace('v4.viki.io','http')
                    #xbmc.executebuiltin("Notification(VIKI®,DASH Streaming: 480p,2000)")
                #elif quality == '1': #Direct MP4 360p
                    #domain = re.search('//(.+?)/', jsonrsp['360p']['https']['url']).group(1)
                    #stream = jsonrsp['360p']['https']['url'].replace(domain,'content.viki.com').replace('https','http')
                    #xbmc.executebuiltin("Notification(VIKI®,MP4 Progressive Download,2000)")
            #	else: #Direct MP4 480p
                    #domain = re.search('//(.+?)/', jsonrsp['480p']['https']['url']).group(1)
            #		stream = jsonrsp['480p']['https']['url'] #.replace(domain,'content.viki.com') #.replace('https','http')
            #		xbmc.executebuiltin("Notification(VIKI®,MP4 Progressive Download,2000)")

            #else:
                #xbmc.executebuiltin("Notification(VIKI®,The addon needs rewriting!!!,2000)")

            except HTTPError as e:
                xbmcgui.Dialog().ok('VIKI® Error',str(e.code)+" "+str(e.reason)+"\n"+"That's all we know about this error.")
            except URLError as e:
                xbmcgui.Dialog().ok('VIKI® Error',str(e.code)+" "+str(e.reason)+"\n"+"That's all we know about this error.")
        #Jeśli debugowanie jest dozwolone
        #else:
        #	xbmc.executebuiltin("Notification(VIKI®,Debug mode is no longer supported <!>,8000)")


        #Prośba o otrzymanie strumienia wideo ze strony
        #request_headers = {
        #"Host": "www.viki.com",
        #"User-Agent": UA,
        #"Accept": "application/json, text/plain, */*",
        #"Accept-Language": "en-US;q=0.7,en;q=0.3",
        #"Referer": "https://www.viki.com/videos/",
        #"x-viki-app-ver": "4.0.80",
        #"x-client-user-agent": UA,
        #"Connection": "keep-alive",
        #"Sec-Fetch-Dest": "empty",
        #"Sec-Fetch-Mode": "cors",
        #"Sec-Fetch-Site": "same-origin",
        #"TE": "trailers"
        #}

        #response = requests.get('https://www.viki.com/api/videos/'+url, headers=request_headers)
        #jsonrsp = response.json()
        #print ((base64.b64decode(jsonrsp['streams']['dash']['url'].replace('https://0.viki.io/b/e-stream-url?stream=','').encode('ascii'))).decode('ascii'))
        #stream = base64.b64decode(jsonrsp['streams']['dash']['url'].replace('https://0.viki.io/b/e-stream-url?stream=','').encode('ascii')).decode('ascii')




        #Ładowanie wideo
        try:
            #print stream
            if 'manifest_url' not in test:
                stream = stream+'|verifypeer=false&User-Agent='+ quote_plus(MUA)+'&Referer=https://www.viki.com'
                li = xbmcgui.ListItem(path=stream1)
                li.setArt({'thumb': thumbnail,'poster': thumbnail, 'banner': thumbnail, 'fanart': thumbnail, 'icon': thumbnail})
                li.setInfo(type="Video", infoLabels={ 'Title': name, 'Plot': plot})


            if 'manifest_url' in test:

                is_helper = inputstreamhelper.Helper('mpd', drm='com.widevine.alpha')
                if is_helper.check_inputstream():
                    if manifest: #Jeśli API zwróci wynik/manifest
                        #li = xbmcgui.ListItem(path=jsonrsp['mpd']['http']['url'])
                        li = xbmcgui.ListItem(path=stream1)
                        li.setArt({'thumb': thumbnail, 'poster': thumbnail, 'banner' : thumbnail, 'fanart': thumbnail, 'icon': thumbnail })
                        li.setInfo(type="Video", infoLabels={ 'Title': name, 'Plot': plot } )

                        li.setMimeType('application/xml+dash')
                        li.setContentLookup(False)

                        li.setProperty('inputstream', 'inputstream.adaptive')
                        li.setProperty('inputstream.adaptive.manifest_type', 'mpd')

                        #li.setProperty('inputstream.adaptive.license_type', 'com.widevine.alpha')

                        #li.setProperty('inputstream.adaptive.license_key', manifest + '||R{SSM}|')
                        #li.setProperty('inputstream.adaptive.license_key', 'https://manifest-viki.viki.io/v1/license?dt=dt3&video_id='+test2+'&app=100000a&app_ver=4.0.80|User-Agent='+ quote_plus(UA)+'&Origin=https://www.viki.com&Referer=https://www.viki.com|R{SSM}|')
                        #li.setProperty('inputstream.adaptive.stream_headers', 'User-Agent='+ quote_plus(UA)+'&Origin=https://www.viki.com&Referer=https://www.viki.com&verifypeer=false')

                    else:
                        xbmc.executebuiltin('Notification(%s, %s, %d, %s)'%('VIKI®','API does not return a result', 4000, md+'OverlayLocked.png'))

            #Ustaw napisy, jeśli są, lub wyłącz je
            if (sub=='true'):
                li.setSubtitles([srtsubs_path])
                #while not xbmc.Player().isPlaying():
                #	xbmc.sleep(1000) #wait until video is being played
                #	xbmc.Player().setSubtitles(srtsubs_path)
            else:
                xbmc.Player().showSubtitles(False)
            xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, listitem=li)

        except HTTPError as e:
            xbmcgui.Dialog().ok('VIKI® Error',str(e.code)+" "+str(e.reason)+"\n"+"That's all we know about this error.")
        except URLError as e:
            xbmcgui.Dialog().ok('VIKI® Error',str(e.code)+" "+str(e.reason)+"\n"+"That's all we know about this error.")

#Moduł do dodawania osobnego tytułu i jego atrybutów do zawartości katalogu wyświetlanego w Kodi - TUTAJ NIE TRZEBA ZMIENIAĆ
def addLink(name,url,vd,hd,plot,author,rating,ar,action,iconimage):

    trans = ''
    try:
        trans = language + ' ' + url.split('@')[2] + '%'
    except:
        pass
#	try:
#		name = control.lang(name).encode("utf-8")
#	except:
    u=sys.argv[0]+"?url="+ quote_plus(url)+"&action="+str(action)+"&name="+ quote_plus(name)


    #ok=True
    liz=xbmcgui.ListItem(name)
    liz.setArt({'thumb': iconimage, 'poster': iconimage, 'banner': iconimage, 'fanart': iconimage, 'icon': iconimage})
    liz.setInfo(type="Video", infoLabels={"Title": name, "Rating": ar})
    liz.setInfo(type="Video", infoLabels={"Duration": vd, "Plot": plot})
    if trans:
        liz.setInfo(type="Video", infoLabels={'code': trans})
    #liz.setInfo( type="Video", infoLabels={ "PlotOutline": "Това е plotoutline", "Tagline": "Това е tagline" } )
    liz.setInfo( type="Video", infoLabels={ "Studio": author, "Mpaa": rating } )
    if hd=='True':
        liz.addStreamInfo('video', { 'width': 1280, 'height': 720 })
        liz.addStreamInfo('video', { 'aspect': 1.78, 'codec': 'h264' })
    else:
        liz.addStreamInfo('video', { 'width': 720, 'height': 480 })
        liz.addStreamInfo('video', { 'aspect': 1.5, 'codec': 'h264' })
    liz.addStreamInfo('audio', { 'codec': 'aac', 'channels': 2 })
    liz.setProperty("IsPlayable" , "true")

    contextmenu = []
    contextmenu.append(('Information', 'XBMC.Action(Info)'))
    liz.addContextMenuItems(contextmenu)
    xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=False)
    xbmcplugin.addSortMethod(int(sys.argv[1]), sortMethod=xbmcplugin.SORT_METHOD_UNSORTED,
                             label2Mask='%P '+' %D')

    #ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=False)
    #return ok
#    Moduł dodawania osobnego katalogu i jego atrybutów do zawartości katalogu wyświetlanego w Kodi - TUTAJ NIE TRZEBA ZMIENIAĆ
def addDir(name,url,plot,action,iconimage):
#	try:
#		name = control.lang(name).encode("utf-8")
#	except:

    u = sys.argv[0]+"?url=" + quote_plus(url) + "&action="+str(action)+ "&name=" + quote_plus(name)
    ok=True
    liz=xbmcgui.ListItem(name)
    liz.setArt({'thumb': iconimage, 'poster': iconimage, 'banner': iconimage, 'fanart': iconimage, 'icon':'DefaultFolder.png'})
    liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": plot})

    if len(plot)>0:
        contextmenu = []
        contextmenu.append(('Information', 'XBMC.Action(Info)'))
        liz.addContextMenuItems(contextmenu)

    ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
    return ok


#TUTAJ NIE TRZEBA NIC ZMIENIAĆ



name = params.get("name")
url = params.get("url")
iconimage = params.get("iconimage")
action = params.get("action")

#Lista poszczególnych podprogramów/modułów w tej wtyczce - musi być w pełni zgodna z powyższym kodem
if action == None:
    CATEGORIES()
elif action == 'index':
    INDEX(url)
elif action == 'prepare':
    PREPARE(url)
elif action == 'search':
    SEARCH()
elif action == 'movieSearchnew':
    search_new(SEARCH_URL)
elif action == "movieSearchterm":
    search_term(SEARCH_URL, name)
elif action == 'play':
    PLAY(name,url,iconimage)
elif action == 5:
    SIGN(url,pth)
elif action == 'genre':
    GENRE(url)
elif action == 'country':
    COUNTRY(url)
elif action == 'loadID':
    LOADBYID()


xbmcplugin.endOfDirectory(int(sys.argv[1]))
