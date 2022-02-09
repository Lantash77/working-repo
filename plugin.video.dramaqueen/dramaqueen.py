# -*- coding: UTF-8 -*-
#####Python3.6

import re
import sys
import time
import os
import threading
import requests
import json
import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon
import xbmcvfs
from urllib.parse import quote_plus
from resources.libs.CommonFunctions import parseDOM
from resources.libs import cache
from resources.libs import addon_tools as addon
from resources.libs import dqscraper
my_addon = xbmcaddon.Addon()
my_addon_id = my_addon.getAddonInfo('id')
DATA_PATH = xbmcvfs.translatePath(my_addon.getAddonInfo("profile"))
setting = my_addon.getSetting
PATH = my_addon.getAddonInfo('path')
MEDIA = xbmcvfs.translatePath('special://home/addons/' + my_addon_id + '/media/')

searchFile = os.path.join(DATA_PATH, "search.db")
base_link = "https://dramaqueen.pl/"
setting = xbmcaddon.Addon().getSetting
search_url = 'https://www.dramaqueen.pl/?s=%s'
sess = requests.session()

headersget = {
    'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Mobile Safari/537.36 Edg/97.0.1072.69'
}

DKorea = 'Drama Koreańska'
DJapan = 'Drama Japońska'

############################################################################################################
############################################################################################################
#                                                   MEDIA                                                  #
############################################################################################################
korea_background = MEDIA + 'Korea.jpg'
japan_background = MEDIA + 'Japan.jpg'
china_background = MEDIA + 'China.jpg'
korea_thumb = MEDIA + 'koreathumb.png'
japan_thumb = MEDIA + 'japoniathumb.png'
inne_thumb = MEDIA + 'innethumb.png'
default_background = MEDIA + 'search.jpg'
search_icon = MEDIA + 'search.png'
iconsettings = MEDIA + 'settings.png'

############################################################################################################
############################################################################################################
#                                                   MENU                                                   #
############################################################################################################

def CATEGORIES(login):

    addon.addDir('[COLOR=%s]Gatunki[/COLOR]' % 'yellow',
                 base_link,
                 mode=4, fanart=korea_background)  
    addon.addDir(str(DKorea),
                 base_link + 'drama/koreanska/',
                 mode=1, fanart=korea_background, thumb=korea_thumb)
    addon.addDir(str(DJapan),
                 base_link + 'drama/japonska/',
                 mode=1, fanart=japan_background, thumb=japan_thumb)
    addon.addDir('Dramy Inne',
                 base_link + 'drama/pozostale/',
                 mode=1, fanart=china_background, thumb=inne_thumb)
    addon.addDir('Film Korea',
                 base_link + 'film/koreanski/',
                 mode=1, fanart=korea_background, thumb=korea_thumb)
    addon.addDir('Film Japonia',
                 base_link + 'film/japonski/',
                 mode=1, fanart=japan_background, thumb=japan_thumb)
    addon.addDir('Filmy Pozostałe',
                 base_link + 'film/pozostale/',
                 mode=1, fanart=china_background, thumb=inne_thumb)
    addon.addDir("Wyszukiwanie", 'https://www.dramaqueen.pl/?s=',
                 mode=6, fanart=default_background, thumb=search_icon)
###Ustawienia###
    addon.addDir('Ustawienia', '', mode=12,
                 fanart=default_background, thumb=iconsettings, isFolder=True)

    if login == True:
       Logowanie(True)
############################################################################################################
#=##########################################################################################################
#                                                 FUNCTIONS                                                #
#=##########################################################################################################

def Logowanie(popup):
   
    headers = {
        'authority': 'www.dramaqueen.pl',
        'cache-control': 'max-age=0',
        'origin': 'https://dramaqueen.pl',
        'scheme': 'https',
        'upgrade-insecure-requests': '1',
        'dnt': '1',
        'content-type': 'application/x-www-form-urlencoded',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.75 Safari/537.36',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'referer': 'https://www.dramaqueen.pl/login/',
        'accept-language': 'pl-PL,pl;q=0.9,en-GB;q=0.8,en;q=0.7,en-US;q=0.6',
                   }
    data = {
        'user_login': setting('user'),
        'login_user_pass': setting('pass'),
        'no_captcha': 'yes',
        'upme-login': 'Log In',
    }
#    sess = requests.session()
    GetLogin = sess.post(base_link + 'login/', headers=headers, data=data)
    response = GetLogin.status_code
    GetLogin = GetLogin.text
    kuki = sess.cookies.items()
    cookie = "; ".join([str(x) + "=" + str(y) for x, y in kuki])
    cache.cache_insert('dramaqueen_cookie', cookie)

###LoginCheck - server error handling    
    if response == 200:
        if len(re.findall('Witaj, ', GetLogin, re.IGNORECASE)) == 1:
            if popup == True:

                dialog = xbmcgui.Dialog()
                dialog.notification('dramaqueen.pl ', 'Zalogowano pomyślnie.', xbmcgui.NOTIFICATION_INFO, 5000, sound=False)
            else:
                pass
        else:
            dialog = xbmcgui.Dialog()
            ret = dialog.yesno('Nie jesteś zalogowany', 'Zarejestruj się na dramaqueen.pl. \nWprowadź dane logowania w ustawieniach wtyczki' ,
                               'Wyjdź', 'Ustawienia')
            if ret:
                my_addon.openSettings()
                xbmc.executebuiltin('Container.Refresh')
    else:
        d = xbmcgui.Dialog()
        d.notification('dramaqueen.pl ',
                       '[COLOR red]%s[/COLOR]' % ('Problem  -  Błąd serwera -' + str(response)),
                       xbmcgui.NOTIFICATION_INFO, 5000)
        exit()
       
def LoginCheck(url):

    if len(re.findall('Witaj,', url, re.IGNORECASE)) == 0:
        xbmcgui.Dialog().ok('Blad logowania', 'Zaloguj się')
        exit()
    
def Kategorie():

    Logowanie(False)
    cookie = cache.cache_get('dramaqueen_cookie')['value']
    headersget.update({'Cookie': cookie})

    url = params['url']

    ht1 = sess.get(url, headers=headersget, timeout=10)

    ht2 = ht1.links['alternate']['url']
    ht3 = json.loads(requests.get(ht2, headers=headersget, timeout=10).text)['content']['rendered']
#    rG = requests.get(url, headers=headersget, timeout=15).text

    result = parseDOM(ht3, 'div', attrs={'class': 'tagcloud'})[0]
    links = parseDOM(result, 'a', ret='href')
    label = parseDOM(result, 'a')

    count = [re.findall('\d+', i)[0] for i in parseDOM(result, 'a', ret='aria-label')]

    for item in zip(label, links, count):
 
        addon.addDir(str(item[0]), str(item[1]), mode=5, fanart='', plot='', 
                    thumb='', code='[B][COLOR %s]%s[/COLOR][/B]' % ('green', str(item[2]) + ' pozycji'))

    xbmcplugin.addSortMethod(int(sys.argv[1]), sortMethod=xbmcplugin.SORT_METHOD_TITLE, 
                             label2Mask= '%P')

def KategorieLista():

    cookie = cache.cache_get('dramaqueen_cookie')['value']
    headersget.update({'Cookie': cookie})

    url = params['url']

    rG = requests.get(url, headers=headersget, timeout=15).text
    rG = CleanHTML(rG)

    result = parseDOM(rG, 'div', attrs={'class': 'avia-content-slider-inner'})[0]
    label = [parseDOM(i, 'a', ret= 'title')[0] for i in parseDOM(result, 'h3')]
    obraz = parseDOM(result, 'img', ret= 'src')
    links = [parseDOM(i, 'a', ret='href')[0] for i in parseDOM(result, 'h3')]

    for item in zip(label, links, obraz):
       if str(item[1]).__contains__('/drama/'):
           addon.addDir(str(item[0]), str(item[1]), subdir=label,
                        mode=2, fanart=str(item[2]), thumb=str(item[2]),
                        code='[B][COLOR %s]Drama[/COLOR][/B]' % 'green')
           
       elif str(item[1]).__contains__('/film/'):
           addon.addLink(str(item[0]), str(item[1]), subdir=label,
                         mode=3, fanart=str(item[2]), thumb=str(item[2]),
                         code='[B][COLOR %s]Film[/COLOR][/B]' % 'green')
           
    xbmcplugin.addSortMethod(int(sys.argv[1]), sortMethod=xbmcplugin.SORT_METHOD_TITLE, 
                             label2Mask= '%P')

def ListTitles():

    Logowanie(False)
    cookie = cache.cache_get('dramaqueen_cookie')['value']
    headersget.update({'Cookie': cookie})

    url = params['url']

    ht1 = sess.get(url, headers=headersget, timeout=10)
    ht2 = ht1.links['alternate']['url']
    ht3 = json.loads(requests.get(ht2, headers=headersget, timeout=10).text)['content']['rendered']
    ht3 = CleanHTML(ht3)

    result = parseDOM(ht3, 'div', attrs={'id': 'av_section_1'})[0]
    res = parseDOM(result, 'div', attrs={'class': 'flex_column ' + r'.+?'})
    left = res[::2]
    right = res[1::2]

    titles = [parseDOM(t, 'p')[0] for t in right]
    linki = [item for item in parseDOM(left, 'a', ret='href')]
    Plot = [parseDOM(t, 'p')[1] for t in right]
    obrazy = [parseDOM(t, 'img', ret='src')[0] for t in left]

    # results = re.findall('flex_column' + pattern + 'av_one_fourth(.+?)</div></div></div>', result)
    # results = re.findall('flex_column '+ r'.+?'+' av_one_fourth (.+?)</div></div></div>', result)
    #
    #
    #
    # html = requests.get(url, headers=headersget, timeout=15).text
    #
    # html = CleanHTML(html)
    #
    # result = parseDOM(html, 'div', attrs={'id': 'av_section_1'})[0]
    # results = re.findall('flex_column av_one_fourth(.+?)</div></div></div>', result)
    #
    # titles = [t for t in re.findall('><p>(.+?)</p>', left)]
    # linki = [item for item in parseDOM(results, 'a', ret='href')]
    # Plot = re.findall('/p>[\s,\S,.]<p>(.+?)</p>', result)
    # obrazy = parseDOM(results, 'img', ret='src')

    threads = []
    meta = {}
    for item in zip(linki, titles, obrazy, Plot):
        # TODO:Scraper via TMDB

        #    title, poster, plot, banner, fanart, genre, year, thread = dqscraper.scraper_check(item[1], item[0], item[2])
        #    if title == '': title = item[1]
        #    if plot == '': plot = item[3]
        #    if poster == '': poster = item[2]
        #    if banner == '': banner = item[2]
        #    if fanart == '': fanart = item[2]
        #    if genre == '': genre = ''
        #    if year == '': year = ''
        #    if thread: threads.append(thread)

        title = item[1]
        plot = item[3]
        poster = item[2]
        banner = item[2]
        fanart = item[2]
        genre = ''
        year = ''
        meta = {'title': title, 'plot': plot, 'poster': poster, 'banner': banner,
                'fanart': fanart, 'genre': genre, 'year': year}

        if str(item[0]).__contains__('/drama/'):
            addon.addDir(str(title), str(item[0]), mode=2, plot=(str(plot)),
                         fanart=(str(fanart)), isFolder=True, thumb=(str(poster)), subdir=title,
                         banner=(str(banner)), genre=str(genre), year=str(year), section='', meta=meta)
        elif str(item[0]).__contains__('/film/'):
            addon.addLink(str(title), str(item[0]), mode=3, plot=str(plot),
                          fanart=str(fanart), thumb=str(poster),
                          banner=str(banner), subdir=title, meta=meta)

    # if thread:
    #    t = threading.Thread(target=scrape_info2, args=(threads,))
    #    if t.is_alive():
    #        t.join()
    #    else:
    #        t.start()


def ListEpisodes():
    Logowanie(False)
    cookie = cache.cache_get('dramaqueen_cookie')['value']
    headersget.update({'Cookie': cookie})    
    
    name = params['name']
    thumb = params['img']
    subdir = params['subdir']
    url = params['url']
    rE = str(requests.get(url, headers=headersget, timeout=15).text)
    rE = CleanHTML(rE)
#    LoginCheck(rE)
    
#    rE = str.replace(rE, '&#8211;', '-')
#    rE = rE.replace('&nbsp;', ' ')
    result = parseDOM(rE, 'div', attrs={'class': 'togglecontainer '+ r'.+?'})[0]
    results = re.findall('av_toggle_section(.+?)<span', result)
    episodes = [item for item in parseDOM(results, 'p')]
    
    plot = parseDOM(rE, 'section', attrs={'class': 'av_textblock_section '})[1]
    if '<em>' in plot:
        plot = CleanHTML(parseDOM(plot, 'em')[0])
    else:
        plot = CleanHTML(parseDOM(plot, 'p')[0])

    fanart = ''#re.findall('background-image: url\((.+?)\);', rE)[1]
    
    inprogress = '[COLOR=red][I]  w tłumaczeniu[/COLOR][/I]'
    incorrection = '[COLOR=red][I]  korekta[/COLOR][/I]'

    for item in episodes:
        if item.__contains__('tłumaczenie'):
            addon.addLink(str(inprogress), url, mode=8, fanart=(str(fanart)), 
                          plot=(str(plot)), thumb=str(thumb))
        elif 'korekta' in item:
            addon.addLink(str(incorrection), url, mode=8, fanart=(str(fanart)), 
                          plot=(str(plot)), thumb=str(thumb))
        else:
            addon.addLink(str(item), url, mode=3, fanart=(str(fanart)), 
                          plot=(str(plot)), thumb=str(thumb), subdir=subdir)
    

def WyswietlanieLinkow():
    Logowanie(False)
    cookie = cache.cache_get('dramaqueen_cookie')['value']
    headersget.update({'Cookie': cookie})

    url = params['url']
    name = params['name']
    subdir = params['subdir']
    html = requests.get(url, headers=headersget, timeout=15).text
    html = html.replace('&#8211;', '-').replace('&nbsp;', ' ')
    LoginCheck(html)
    results = [item for item in parseDOM(html, 'section', attrs={'class': 'av_toggle_section ' +r'.+?'})]
    
    if name.startswith('Odcinek '):
        index = int(re.findall('\d+', name)[0])        
        avlinks = [parseDOM(item, 'a', ret='href')for item in results][index - 1]
        avplayers = [parseDOM(item, 'button')for item in results][index - 1]        
              
    elif 'tłumaczeni' in name:
        pass
    elif 'korekta' in name:
        pass
    else:        
        
        avlinks = [parseDOM(item, 'a', ret='href') for item in results][0]
        avplayers = [parseDOM(item, 'button') for item in results][0]

    for i in avplayers:
        if i == ('DQ - test' or 'DQ-test'):
            test = i
            index = avplayers.index(i)
            avlinks[index] = 'dqplayer|' + avlinks[index]
         
    addon.SourceSelect(players=avplayers, links=avlinks, title=name, subdir=subdir)
    
def Szukaj_Nowy():

#    url = params['url']
    keyb = xbmc.Keyboard('', "Wyszukiwarka")
    keyb.doModal()

    if keyb.isConfirmed() and len(keyb.getText().strip()) > 0:
        search = keyb.getText()
#        url = url % search.replace(" ", "+")

    else: CATEGORIES(False)

    from sqlite3 import dbapi2 as database

    dbcon = database.connect(searchFile)
    dbcur = dbcon.cursor()
    dbcur.execute("INSERT INTO movies VALUES (?,?)", (None, search))
    dbcon.commit()
    dbcur.close()

    search = quote_plus(search)
    url = search_url % search
    WynikiSzukania(url)

def WynikiSzukania(url):

    Logowanie(False)
    cookie = cache.cache_get('dramaqueen_cookie')['value']
    headersget.update({'Cookie': cookie})

    html = requests.get(url, headers=headersget, timeout=15).text

    result = str(parseDOM(html, 'main', attrs={'role': 'main'})[0])
    results = [CleanHTML(item) for item in parseDOM(result, 'h2')]
    
    excludelist = ['Japońsk', 'Koreańsk', 'Pozostałe']
    includelist = ['/drama/', '/film/']
    for item in results:
        if any(exclude in item for exclude in excludelist):
            continue
        elif any(include in item for include in includelist):
            Title = parseDOM(item, 'a')[0]
            link = parseDOM(item, 'a', ret='href')[0]
            data = requests.get(link, headers=headersget, timeout=10).text
#            title, poster, plot, banner, fanart, genre, year, thread = dqscraper.scraper_check(Title, link, poster='')
#            fanart = re.findall('background-image: url\((.+?)\);', data)[1]
            poster = parseDOM(data, 'img', attrs={'itemprop': 'thumbnailUrl'}, ret='src')[0]
            plot = parseDOM(data, 'em')[0]
            plot = CleanHTML(plot)
            title = Title
            fanart = poster
            genre = ''
            year = ''
#            poster, fanart = scraper.Scrap(title, type='drama')
#            if fanart == '':
#                fanart = re.findall('background-image: url\((.+?)\);', data)[1]
#            if poster == '':
#                poster = parseDOM(data, 'img', attrs={'itemprop': 'thumbnailUrl'}, ret='src')[0]
#            if plot == '':
#                plot = parseDOM(data, 'em')[0]
#                plot = CleanHTML(plot)
#            if title == '': title = Title
            
            if '/drama/' in item:
                addon.addDir(str(title), str(link), mode=2, subdir=title,
                            fanart=str(fanart), thumb=str(poster), poster=str(poster),
                            plot=str(plot), code='[B][COLOR=green]drama[/COLOR][/B]',
                            genre=str(genre), year=str(year))
            else:
                addon.addLink(str(title), str(link), mode=3, subdir=title,
                         fanart=str(fanart), thumb=str(poster), poster=str(poster),
                         plot=str(plot), code='[B][COLOR=green]film[/COLOR][/B]',
                         genre=str(genre), year=str(year))                       
                
        else:
            continue
    xbmcplugin.addSortMethod(int(sys.argv[1]), sortMethod=xbmcplugin.SORT_METHOD_TITLE, 
                                 label2Mask= '%P')


def Szukaj():

    addon.addDir("[B]Nowe wyszukiwanie...[/B]", 'https://www.dramaqueen.pl/?s=', mode=11, fanart=default_background, thumb=search_icon)

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
            addon.addDir(term, search_url, mode=9, fanart=default_background, thumb=search_icon)
            lst += [(term)]
    dbcur.close()

    if delete_option:
        addon.addDir("[I]Wyczyść listę wyszukiwania[/I]", '', mode=10, fanart=default_background, thumb=search_icon) #"Naciśnij aby wyczyścić historię"#32605


def search_term(url, name):

    name=quote_plus(name)
    WynikiSzukania(url % name)

def clear_search():

    from sqlite3 import dbapi2 as database
    dbcon = database.connect(searchFile)
    dbcur = dbcon.cursor()
    dbcur.execute("DROP TABLE IF EXISTS %s" % "movies")
    dbcur.execute("VACUUM")
    dbcon.commit()
    dbcur.close()
    Szukaj()


def PathCheck():
    if setting('download.path') == '':
        dialog = xbmcgui.Dialog()
        ret = dialog.yesno('Błąd Ustawień Pobierania',
                           'Włączono pobieranie, ale nie ustawiono ścieżki pobierania \nWprowadź scieżkę pobierania w ustawieniach' ,
                           'Wyjdź', 'Ustawienia')
        if ret:
            my_addon.openSettings()
            xbmc.executebuiltin('Container.Refresh')
        else:
            exit()
    else:
        return



def ScrapInfo(threads):
    while True:
        if xbmc.Player().isPlaying():
            
            for thread in threads:
                while True:
                    if xbmc.Player().isPlaying() and threading.active_count() < 20:
                        time.sleep(2)
                        thread.start()
                        break
                    else:
                        time.sleep(2)
        else:
            time.sleep(2)
            

###Tekstowe###
     
def CleanHTML(html):
    html = str(html)
    if ("&amp;" in html):
        html = html.replace('&amp;', '&')
    if ("&nbsp;" in html):
        html = html.replace('&nbsp;', '')
    if ('&#' in html) and (';' in html):
        if ("&#8211;" in html):
            html = html.replace("&#8211;", "-")
        if ("&#8216;" in html):
            html = html.replace("&#8216;", "'")
        if ("&#8217;" in html):
            html = html.replace("&#8217;", "'")
        if ("&#8220;" in html):
            html = html.replace('&#8220;', '"')
        if ("&#8221;" in html):
            html = html.replace('&#8221;', '"')
        if ("&#0421;" in html):
            html = html.replace('&#0421;', "")
        if (u'\u2019' in html):
            html = html.replace(u'\u2019', '\'')
        if ("&#038;" in html):
            html = html.replace('&#038;', "&")
        if ('&#8230;' in html):
            html = html.replace('&#8230;', '…')
        if ('<br />\n' in html):
            html = html.replace('<br />\n', ' ')
    return html

############################################################################################################
# =#########################################################################################################
#                                               GET PARAMS                                                 #
# =#########################################################################################################

params = addon.get_params()

url = params.get('url')
name = params.get('name')
img = params.get('img')
section = params.get('section')

try:
    mode = int(params.get('mode'))
except:
    mode = None


############################################################################################################
############################################################################################################
#                                                   MODES                                                  #
############################################################################################################

if setting('download.opt') == 'true':
    PathCheck()
if mode == None:
    CATEGORIES(True)
    xbmcplugin.setContent(int(sys.argv[1]), 'movies')
    xbmcplugin.endOfDirectory(int(sys.argv[1]))

elif mode == 1:
    ListTitles()
    xbmcplugin.setContent(int(sys.argv[1]), 'movies')
    xbmcplugin.endOfDirectory(int(sys.argv[1]))

elif mode == 2:
    ListEpisodes()
    xbmcplugin.setContent(int(sys.argv[1]), 'movies')
    xbmcplugin.endOfDirectory(int(sys.argv[1]))

elif mode == 3:
    WyswietlanieLinkow()
    xbmcplugin.setContent(int(sys.argv[1]), 'movies')
    xbmcplugin.endOfDirectory(int(sys.argv[1]))

elif mode == 4:
    Kategorie()
    xbmcplugin.setContent(int(sys.argv[1]), 'movies')
    xbmcplugin.endOfDirectory(int(sys.argv[1]))

elif mode == 5:
    KategorieLista()
    xbmcplugin.setContent(int(sys.argv[1]), 'movies')
    xbmcplugin.endOfDirectory(int(sys.argv[1]))

elif mode == 6:
    Szukaj()
    xbmcplugin.setContent(int(sys.argv[1]), 'movies')
    xbmcplugin.endOfDirectory(int(sys.argv[1]))
    
# Scrapper cleaning
elif mode == 7:
    from resources.libs.dqscraper import delete_table
    delete_table()

# Brak linku - monit
elif mode == 8:
    dialog = xbmcgui.Dialog()
    dialog.notification('dramaqueen.pl ', '[COLOR=red]Brak odcinka.[/COLOR]', xbmcgui.NOTIFICATION_INFO, 5000)
   
elif mode == 9:
    search_term(url, name)
    xbmcplugin.setContent(int(sys.argv[1]), 'movies')
    xbmcplugin.endOfDirectory(int(sys.argv[1]))

elif mode == 10:
     clear_search()
#    xbmcplugin.setContent(int(sys.argv[1]), 'movies')
#    xbmcplugin.endOfDirectory(int(sys.argv[1]))
elif mode == 11:
     Szukaj_Nowy()
     xbmcplugin.setContent(int(sys.argv[1]), 'movies')
     xbmcplugin.endOfDirectory(int(sys.argv[1]))
elif mode == 12:
    my_addon.openSettings()
    xbmc.executebuiltin('XBMC.Container.Refresh()')

############################################################################################################

