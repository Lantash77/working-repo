# -*- coding: utf-8 -*-

"""
    VIKI Rakuten® addon Add-on test
"""

import re
import sys
import os
import time
import json
from urllib.parse import parse_qsl, quote_plus, urlparse, urlunparse, parse_qs, urlencode
from urllib.error import URLError, HTTPError
from resources.libs import lang_sel, common, viki
import requests

import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon
import xbmcgui
import xbmcvfs
import inputstreamhelper
#import YDStreamExtractor


#sys.path.append("C:\Program Files\JetBrains\PyCharm 2021.3\debug-eggs\pydevd-pycharm.egg")
#import pydevd_pycharm
#pydevd_pycharm.settrace('localhost', port=5678, stdoutToServer=True, stderrToServer=True)


my_addon = common.my_addon
my_addon_id = common.my_addon_id
ADDON_PATH = common.ADDON_PATH
DATA_PATH = common.DATA_PATH
MEDIA_PATH = common.MEDIA_PATH
searchFile = common.searchFile
GetSetting = my_addon.getSetting
SetSetting = my_addon.setSetting
md = MEDIA_PATH
MEDIA = {'subtitles': MEDIA_PATH +'DefaultAddonSubtitles.png', 'folder': MEDIA_PATH+'DefaultFolder.png',
         'search': MEDIA_PATH+'DefaultAddonsSearch.png', 'error': MEDIA_PATH+'DefaultIconError.png',
         'back': MEDIA_PATH+'DefaultFolderBack.png', 'studio': MEDIA_PATH+'DefaultStudios.png',
         'locked': MEDIA_PATH+'OverlayLocked.png'}
UA = 'Mozilla/5.0 (Macintosh; MacOS X10_14_3; rv;93.0) Gecko/20100101 Firefox/93.0'
header = {'user-agent': UA}
SEARCH_URL = 'https://api.viki.io/v4/search.json?page=1&per_page=50&app=100000a&term='
BASE_MOVIE_URL = 'https://api.viki.io/v4/movies.json?%s'
BASE_SERIES_URL = 'https://api.viki.io/v4/series.json?%s'
system_lang = xbmc.getLanguage(0, region=True).split('-')[0]
params = dict(parse_qsl(sys.argv[2].replace("?", "")))
L = lang_sel.L
VikiAPI = viki.VikiAPI()

try: lang_code = [i['code'] for i in lang_sel.languagelist if i['lang'] == system_lang][0]
except : lang_code = '0'

t = GetSetting('subs.init')
if GetSetting('subs.init') == '':
   SetSetting('lang', lang_code)
   lang, language = lang_sel.get_lang(lang_code)

   common.dialog.notification(L(32003), L(32123) + language, MEDIA['subtitles'], 5000, sound=False)
   SetSetting('subs.init', 'true')
else:
    lang, language = lang_sel.get_lang()


#Ustaw kolejność odcinków
d =GetSetting('direction')
if d == '0': order = '&direction=desc'
elif d == '1': order = '&direction=asc'

subs_enabled = GetSetting('subs.enabled')

#Main menu
def CATEGORIES():
    addDir(32100, '', 'search', '', MEDIA['search']) #Search
    addDir(32105, 'movies', 'genre', '', MEDIA['folder'])
    addDir(32107, 'movies', '', 'country', MEDIA['folder'])
    addDir(32108, BASE_MOVIE_URL % 'sort=newest_video&page=1&per_page=50&app=100000a&t=', 'index', '', MEDIA['folder'])
    addDir(32109, BASE_MOVIE_URL % 'sort=trending&page=1&per_page=50&app=100000a&t=', 'index', '', MEDIA['folder'])
    addDir(32110, BASE_MOVIE_URL % 'sort=views&page=1&per_page=50&app=100000a&t=', 'index', '', MEDIA['folder'])
    addDir(32111, BASE_MOVIE_URL % 'sort=views_recent&page=1&per_page=50&app=100000a&t=', 'index', '',MEDIA['folder'])
    addDir(32112, 'series', 'genre', '', MEDIA['folder'])
    addDir(32113, 'series', 'country', '', MEDIA['folder'])
    addDir(32114, BASE_SERIES_URL % 'sort=newest_video&page=1&per_page=50&app=100000a&t=', 'index', '', MEDIA['folder'])
    addDir(32115, BASE_SERIES_URL % 'sort=trending&page=1&per_page=50&app=100000a&t=', 'index', '', MEDIA['folder'])
    addDir(32116, BASE_SERIES_URL % 'sort=views&page=1&per_page=50&app=100000a&t=', 'index', '', MEDIA['folder'])
    addDir(32117, BASE_SERIES_URL % 'sort=views_recent&page=1&per_page=50&app=100000a&t=', 'index', '', MEDIA['folder'])
    addDir(32118, BASE_SERIES_URL % 'sort=newest_video&page=1&per_page=50&app=100000a&t=', 'index', '', MEDIA['folder'])

def INDEX(url):

    timestamp = str(int(time.time()))

    try:
        if 'search.json' in url:
            jsonrsp = requests.get(url, headers=header, timeout=5).json()
        else:
            jsonrsp = requests.get(url+timestamp, headers=header, timeout=5).json()

        for movie in range(0, len(jsonrsp['response'])):
                data = jsonrsp['response'][movie]
                if (data['flags']['licensed'] == True):
                    if data['type'] == 'series': #Jeśli to seria
                        try: #Tytuł w języku angielskim
                            title = str(data['titles']['en'])
                        except:
                            title = 'TV Show Title'
                        try: #Opis w języku angielskim
                            mdes = str(data['descriptions']['en'])
                        except:
                            mdes = ''
                        try: #Poster
                            pos = data['images']['poster']['url']
                        except:
                            pos = ''
                        try:
                            origin_country = data['origin']
                        except:
                            origin_country = ''
                        try:
                            year = re.search(r'[0-9]{4}', data['created_at']).group(0)
                        except:
                            year = ''
                        try:  # Napisy lokalne
                            subs_local = str(data['subtitle_completions'][lang])
                        except:
                            subs_local = '0'

                        xbmcplugin.setContent(int(sys.argv[1]), 'season')

                        meta = {
                            'title': title,
                            'original_title': '',
                            'origin_country': origin_country,
                            'year': year,
                            'local_subtitle': subs_local,
                            'plot': mdes,
                            'poster': pos,
                        }
                        sysurl = 'https://api.viki.io/v4/series/'+data['id']+'/episodes.json?page=1&per_page=50&app=100000a&t='+timestamp
                        addDir(title, sysurl, 'prepare', mdes, pos, code=subs_local)

                    else: #Jeśli jest to film fabularny lub wideo
                        if (data['blocked'] == False):
                            try: #Napisy lokalne
                                subs_local = str(data['subtitle_completions'][lang])
                            except:
                                subs_local = '0'
                            try: #angielskie napisy
                                subs_en = str(data['subtitle_completions']['en'])
                            except:
                                subs_en = '0'
                            try: #Czas trwania filmu
                                dur = str(data['duration'])
                            except:
                                dur = ''
                            try: #Rozdzielczość wideo
                                quality = str(data['flags']['hd'])
                            except:
                                quality = 'False'
                            try: #Nazwa / opis filmu
                                title = str(data['titles']['en'])
                            except:
                                title = 'Movie Title'
                            try: #Autor / Studio
                                author = str(data['author'])
                            except:
                                author = ''
                            try: #Movie ID
                                movie_ID = str(data['id'])
                            except:
                                movie_ID = ''
                            try: #Poster
                                poster = str(data['images']['poster']['url'])
                            except:
                                poster = ''
                            try: #Ocena
                                rating = data['rating']
                            except:
                                rating = 'G'
                            try: #Stopień
                                ar = str(data['container']['review_stats']['average_rating'])
                            except:
                                ar = '0'

                            meta = {
                                'title': title,
                                'movieID': movie_ID,
                                'original_title': '',
                                #'origin_country': origin_country,
                                #'year': year,
                                'quality': quality,
                                'local_subs': subs_local,
                                'en_subs': subs_en,
                                'poster': poster,
                                'duration': 'duration'
                            }
                            xbmcplugin.setContent(int(sys.argv[1]), 'movie')
                            sysurl = movie_ID +'@'+poster+'@'+subs_local+'@'+subs_en+'@'+title
                            addLink(title, sysurl, dur, quality, title, author, rating, ar, 'play', poster, meta)


    except:
        pass

    #next page...
    if jsonrsp['more'] == True:

        fronturl, page, backurl = re.findall('(.+?)&page=(.+?)&per_page=(.+?)&t=', url)[0]
        newpage = int(page) + 1
        url = fronturl + '&page=' + str(newpage) + '&per_page=' + backurl + '&t='
        addDir(32120, url, 'index', '', md + 'DefaultFolder.png')

#Przeglądanie odcinków serialu
def PREPARE(url):

    xbmcplugin.setContent(int(sys.argv[1]), 'episode')
    timestamp = str(int(time.time()))
    jsonrsp = requests.get(url + order, headers=header).json()

    for episode in range(0, len(jsonrsp['response'])):
        data = jsonrsp['response'][episode]
        try:
            if (data['blocked'] == False):
                try: #Nazwa serii
                    tsn = str(data['container']['titles']['en'])
                except:
                    tsn = ''
                try: #Numer odcinka serialu
                    ep_no = L(32121) + str(data['number'])
                except:
                    ep_no = ''
                try: #Identyfikator odcinka
                    video_id = str(data['id'])
                except:
                    video_id = ''
                try: #Poster URL
                    pos = str(data['images']['poster']['url'])
                except:
                    pos = ''
                try: #Duration
                    dur = str(data['duration'])
                except:
                    dur = ''
                try: #Średnia ocena
                    ar = str(data['container']['review_stats']['average_rating'])
                except:
                    ar = ''
                try: #Napisy lokalne
                    subs_local = str(data['subtitle_completions'][lang])
                except:
                    subs_local = '0'
                try: #angielskie napisy
                    subs_en = str(data['subtitle_completions']['en'])
                except:
                    subs_en = '0'
                try: #Rozdzielczość wideo
                    hd = str(data['flags']['hd'])
                except:
                    hd = 'False'
                try: #Nazwa / opis odcinka
                    et = str(data['titles'][lang])
                except:
                    et = ''
                try: #Autor / Studio
                    at = str(data['author'])
                except:
                    at = ''
                try: #Ocena
                    rating = str(data['rating'])
                except:
                    rating = 'G'

                sysurl = video_id +'@'+pos+'@'+subs_local+'@'+subs_en+'@'+et
                addLink(tsn + ep_no, sysurl,dur,hd,et,at,rating,ar,'play',pos)

        except:
            common.dialog.notification(L(32003), L(32125), MEDIA['error'], 4000)

    if len(jsonrsp['response'])==0:
        addDir(32122, '', '', '', MEDIA['back'])
    #Koniec indeksowania

    #Next page...
    if jsonrsp['more'] == True:
        getpage=re.compile('(.+?)page=(.+?)&per_page').findall(url)
        for fronturl,page in getpage:
            newpage = int(page)+1
            url = fronturl + 'page=' + str(newpage) + '&per_page=50&app=100000a&t=' + timestamp
            #print 'URL OF THE NEXT PAGE IS' + url
            addDir(32120, url, 'prepare', '', MEDIA['folder'])

#Gatunki
def GENRE(url):

    xbmcplugin.setContent(int(sys.argv[1]), 'season')
    link = 'https://api.viki.io/v4/videos/genres.json?app=100000a'
    jsonrsp = requests.get(link + order, headers=header).json()

    for genre in range(0, len(jsonrsp)):
        addDir(jsonrsp[genre]['name']['en'], 'https://api.viki.io/v4/'+url+'.json?sort=newest_video&page=1&per_page=50&app=100000a&genre='+jsonrsp[genre]['id']+'&t=', 'index', '', MEDIA['folder'])

#Kraj
def COUNTRY(url):
    xbmcplugin.setContent(int(sys.argv[1]), 'season')
    link = 'https://api.viki.io/v4/videos/countries.json?app=100000a'

    jsonrsp = requests.get(link + order, headers=header).json()

    for country, subdict in jsonrsp.items():
        addDir(jsonrsp[country]['name']['en'], 'https://api.viki.io/v4/'+url+'.json?sort=newest_video&page=1&per_page=50&app=100000a&origin_country='+country+'&t=', 'index', '',MEDIA['folder'])

def SEARCH():

    addDir(32103, '', "movieSearchnew", '', MEDIA['search']) #"[B]New search...[/B]
    addLink(32102, 'loadbyid', '0', 'True', '', '', 'G', '5.0', 'loadID', MEDIA['studio'])

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
    try:
        for (id, term) in dbcur.fetchall():
            if term not in str(lst):
                delete_option = True
                addDir(term, "", "movieSearchterm&name=%s" % term, "", MEDIA['search'])
                lst += [(term)]
    except:
        pass
    dbcur.close()

    if delete_option:
        addDir(32119, '', "clearCacheSearch", '', MEDIA['search'])

def search_new(url):

    xbmcplugin.setContent(int(sys.argv[1]), 'season')
    k = xbmc.Keyboard('', L(32000))
    k.doModal()
    q = k.getText() if k.isConfirmed() else None
    if q is None or q == "":
        addDir(32001, '', '', '', MEDIA['back'])

    from sqlite3 import dbapi2 as database

    dbcon = database.connect(searchFile)
    dbcur = dbcon.cursor()
    dbcur.execute("INSERT INTO movies VALUES (?,?)", (None, q))
    dbcon.commit()
    dbcur.close()

    q = quote_plus(q)
    INDEX(url + q)

def search_term(url, name):

    INDEX(url + quote_plus(name))

def clear_search():

    from sqlite3 import dbapi2 as database
    dbcon = database.connect(searchFile)
    dbcur = dbcon.cursor()
    dbcur.execute("DROP TABLE IF EXISTS %s" % "movies")
    dbcur.execute("VACUUM")
    dbcon.commit()
    dbcur.close()
    SEARCH()

#Załaduj klip według ID
def LOADBYID():

    dialog = xbmcgui.Dialog()
    vid = dialog.numeric(0, L(32002))
    if vid != '':
        PLAY('VIKI®', vid+'v@@0@50@', MEDIA['studio'])
    else:
        addDir(32001, '', '', '', MEDIA['back'])

def PLAY(name,url,iconimage):

    ll = parse_qsl(sys.argv[2])

    video_id, thumbnail, subtitle_local, subtitle_en, plot = url.split("@")

    #Pobieranie napisów
    try:
        #Jeśli przetłumaczone ponad 79% napisów w lokalnym języku
        if (int(subtitle_local)>79 and subs_enabled=='true'):
            srtsubs_path = xbmcvfs.translatePath('special://temp/vikirakuten.' + language +'.srt')

            subs = VikiAPI.get_subs(video_id, lang)
            f = xbmcvfs.File(srtsubs_path, 'w')
            f.write(subs)
            f.close()
            sub = 'true'
        #Pobrane napisy w języku angielskim, gdy tłumaczenie niewystarczające
        elif (int(subtitle_en)>0 and subs_enabled=='true'):
            srtsubs_path = common.srtsubs_path
            subs = VikiAPI.get_subs(video_id, 'en')
            f = xbmcvfs.File(srtsubs_path, 'w')
            f.write(subs)
            f.close()
            common.dialog.notification(L(32003), L(32124), MEDIA['subtitles'], 4000)

            sub = 'true'
        else:
            sub = 'false' #Jeśli nie są dostępne napisy
            common.dialog.notification(L(32003), L(32004), MEDIA['subtitles'], 4000)

    except:
        sub = 'false' #Jeśli wystąpił błąd w pobieraniu napisów
        common.dialog.notification(L(32003), L(32005), MEDIA['error'], 4000)

    try:
        ## youtube-dl
        #web = 'https://www.viki.com/videos/' + url + '-viki-link'
        #vid = YDStreamExtractor.getVideoInfo(web,quality=1) #quality is 0=SD, 1=720p, 2=1080p and is a maximum
        #test = vid._streams

        ## Independent API
        manifest, lic = VikiAPI.get_stream(video_id)

        stream = manifest[0]

    except HTTPError as e:
        xbmcgui.Dialog().ok('VIKI® Error',str(e.code)+" "+str(e.reason)+"\n"+"That's all we know about this error.")
    except URLError as e:
        xbmcgui.Dialog().ok('VIKI® Error',str(e.code)+" "+str(e.reason)+"\n"+"That's all we know about this error.")

    #Ładowanie wideo
    try:
        PROTOCOL = 'mpd'
        DRM = 'com.widevine.alpha'
        is_helper = inputstreamhelper.Helper(PROTOCOL)
        if is_helper.check_inputstream():

            if stream: #Jeśli API zwróci wynik/manifest

                import ssl
                try:
                    _create_unverified_https_context = ssl._create_unverified_context
                except AttributeError:
                    pass
                else:
                    ssl._create_default_https_context = _create_unverified_https_context
                certificate_data = "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 VsLobiUUxUx2s1Y//+knyk7clpgw7dzQJd+q"

                li = xbmcgui.ListItem(path=stream)
                li.setArt({'thumb': thumbnail, 'poster': thumbnail, 'banner' : thumbnail, 'fanart': thumbnail, 'icon': thumbnail })
                li.setInfo(type="Video", infoLabels={'Title': name, 'Plot': plot})

                li.setMimeType('application/xml+dash')
                li.setContentLookup(False)

                li.setProperty('inputstream', 'inputstream.adaptive')
                li.setProperty('inputstream.adaptive.manifest_type', PROTOCOL)
                li.setProperty('inputstream.adaptive.license_type', DRM)
                li.setProperty('inputstream.adaptive.server_certificate', certificate_data)

                #li.setProperty('inputstream.adaptive.license_key', stream + '||R{SSM}|')
                li.setProperty('inputstream.adaptive.license_key', lic['dt3']+'|User-Agent='+ quote_plus(UA)+'&Origin=https://www.viki.com&Referer=https://www.viki.com|R{SSM}|')
                #li.setProperty('inputstream.adaptive.stream_headers', 'User-Agent='+ quote_plus(UA)+'&Origin=https://www.viki.com&Referer=https://www.viki.com&verifypeer=false')

            else:
                common.dialog.notification(L(32003), L(32126), MEDIA['locked'], 4000)

        #subtitles on
        if (sub=='true'):
            li.setSubtitles([srtsubs_path])

        else:
            xbmc.Player().showSubtitles(False)
        xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, listitem=li)

    except HTTPError as e:
        xbmcgui.Dialog().ok('VIKI® Error',str(e.code)+" "+str(e.reason)+"\n"+"That's all we know about this error.")
    except URLError as e:
        xbmcgui.Dialog().ok('VIKI® Error',str(e.code)+" "+str(e.reason)+"\n"+"That's all we know about this error.")


def addLink(name, url, vd, hd, plot, author, rating, ar, action, iconimage, meta={}):

    if isinstance(name, int):
        name = L(name)

    trans = ''
    try:
        trans = language + ' ' + url.split('@')[2] + '%'
    except:
        pass

    u = sys.argv[0]+"?url="+ quote_plus(url)+"&action="+str(action)+"&name="+ quote_plus(name)

    liz = xbmcgui.ListItem(name)
    liz.setArt({'thumb': iconimage, 'poster': iconimage, 'banner': iconimage, 'fanart': iconimage, 'icon': iconimage})
    info = {
        "Title": name,
        "Rating": ar,
        "Duration": vd,
        "Plot": plot,
        "code": trans,
        "Studio": author,
        "Mpaa": rating
    }
    liz.setInfo(type="Video", infoLabels=info)

    if hd == 'True':
        liz.addStreamInfo('video', {'width': 1280,
                                    'height': 720,
                                    'aspect': 1.78,
                                    'codec': 'h264'
                                    }
        )
    else:
        liz.addStreamInfo('video', {'width': 720,
                                    'height': 480,
                                    'aspect': 1.5,
                                    'codec': 'h264'
                                    }
                          )

    liz.addStreamInfo('audio', {'codec': 'aac', 'channels': 2})
    liz.setProperty("IsPlayable", "true")

    contextmenu = []
    contextmenu.append(('Information', 'XBMC.Action(Info)'))
    liz.addContextMenuItems(contextmenu)
    xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=False)
    xbmcplugin.addSortMethod(int(sys.argv[1]), sortMethod=xbmcplugin.SORT_METHOD_UNSORTED,
                             label2Mask='%P '+' %D')



def addDir(name, url,  action, plot, iconimage, code='', meta={}):
    if isinstance(name, int):
        name = L(name)
    if code:
        code = language + ' ' + code + '%'

    u = sys.argv[0]+"?url=" + quote_plus(url) + "&action="+str(action)+ "&name=" + quote_plus(name)

    liz=xbmcgui.ListItem(name)

    liz.setArt({'thumb': iconimage, 'poster': iconimage, 'banner': iconimage, 'fanart': iconimage, 'icon':'DefaultFolder.png'})
    info = {
        "Title": name,
        "Plot": plot,
        "code": code
    }

    liz.setInfo(type="Video", infoLabels=info)

    if len(plot)>0:
        contextmenu = []
        contextmenu.append(('Information', 'XBMC.Action(Info)'))
        liz.addContextMenuItems(contextmenu)

    xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
    xbmcplugin.addSortMethod(int(sys.argv[1]), sortMethod=xbmcplugin.SORT_METHOD_UNSORTED,
                             label2Mask='%P ')

#
#  MODES
#
name = params.get("name")
url = params.get("url")
iconimage = params.get("iconimage")
meta = params.get("meta")
action = params.get("action")


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
elif action == 'clearCacheSearch':
    clear_search()
elif action == 'play':
    PLAY(name,url,iconimage)
elif action == 'genre':
    GENRE(url)
elif action == 'country':
    COUNTRY(url)
elif action == 'loadID':
    LOADBYID()

xbmcplugin.endOfDirectory(int(sys.argv[1]))
