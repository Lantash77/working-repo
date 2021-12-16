# -*- coding: UTF-8 -*-
import sys
import re
import urllib.request, urllib.parse, urllib.error
from urllib.parse import parse_qs, quote_plus
import xbmc
import xbmcgui
import xbmcplugin


def addDir(name, url, mode='', icon='', thumb='', fanart='', poster='', banner='', clearart='', clearlogo='',
           genre='', year='', rating='', dateadded='', plot='',
           section='', page='', code='', studio='', meta='',
           isFolder=True, total=1):
    u = (sys.argv[0] + '?url=' + quote_plus(url) + '&mode=' + str(mode) + '&name='
         + quote_plus(name) + '&img=' + quote_plus(thumb)
         + '&section=' + quote_plus(section) + '&page=' + quote_plus(page))
    liz = xbmcgui.ListItem(name)
    contextmenu = []
    contextmenu.append(('Informacja', 'Action(Info)'), )    
    info = {
        'title': name,
        'genre': genre,
        'year': year,
        'rating': rating,
        'dateadded': dateadded,
        'plot': plot,
        'code': code,
        'studio': studio
    }
    liz.setInfo(type='video', infoLabels=info)
    liz.setArt({
        'thumb': thumb,
        'icon': icon,
        'fanart': fanart,
        'poster': poster,
        'banner': banner,
        'clearart': clearart,
        'clearlogo': clearlogo,
    })
    liz.addContextMenuItems(contextmenu)
    xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz,
                                isFolder=isFolder, totalItems=total)


def addLink(name, url, mode='', icon='', thumb='', fanart='', poster='',
            banner='', clearart='', clearlogo='', genre='', year='',
            rating='', dateadded='', plot='', code='', studio='',meta='',
            isFolder=False, total=1,
            type='video', section='', page=''):
    u = (sys.argv[0] + '?url=' + quote_plus(url) + '&mode=' + str(mode)
         + '&name=' + quote_plus(name) + '&img=' + quote_plus(thumb)
         + '&section=' + quote_plus(section) + '&page=' + quote_plus(page))
    liz = xbmcgui.ListItem(name)
    contextmenu = []
    contextmenu.append(('Informacja', 'Action(Info)'), )
    info = {
        'title': name,
        'plot': plot,
        'code': code,
        'studio': studio,
        'genre': genre,
        'rating': rating,
        'year': year,
        'dateadded': dateadded,
    }
    liz.setProperty('IsPlayable', 'true')
    liz.setInfo(type, infoLabels=info)
    liz.setArt({
        'thumb': thumb,
        'icon': icon,
        'fanart': fanart,
        'poster': poster,
        'banner': banner,
        'clearart': clearart,
        'clearlogo': clearlogo
    })

    liz.addContextMenuItems(contextmenu)
    xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz,
                                isFolder=isFolder, totalItems=total)


def get_params():
    paramstring = sys.argv[2]
    if paramstring.startswith('?'):
        paramstring = paramstring[1:]
    return dict((k, vv[0]) for k, vv in parse_qs(paramstring).items())

def PlayFromHost(url, mode, title):


    if 'google' in url:
        url = url.replace('preview', 'view')
#DQ Player    
    try:
        if 'https://dramaqueen.pl/player.php' in url:

            pattern = r'https://(.+?)url='
            videolink = re.sub(pattern, '', url)
            
            li = xbmcgui.ListItem(title, path=str(videolink))
            xbmcplugin.setResolvedUrl(handle=int(sys.argv[1]), succeeded=True, listitem=li)
#Send to resolver           
        else:
            import resolveurl
            try:
                stream_url = resolveurl.resolve(url)
                xbmc.log('DramaQueen.pl | wynik z resolve  : %s' % stream_url, xbmc.LOGINFO)
                li = xbmcgui.ListItem(title, path=str(stream_url))
                xbmcplugin.setResolvedUrl(handle=int(sys.argv[1]), succeeded=True, listitem=li)
            except:
                exit()
                
    except:
        d = xbmcgui.Dialog()
        d.notification('dramaqueen.pl ', 
                       '[COLOR red]Problem  -  Nie można wyciągnąć linku[/COLOR]', 
                       xbmcgui.NOTIFICATION_INFO, 5000)
                                     
def SourceSelect(players, links, title):
    
    if len(players) > 0:
        d = xbmcgui.Dialog()
        select = d.select('Wybór playera', players)
        if select > -1:
            link = str(links[select])
            xbmc.log('DramaQueen.pl | Proba z : %s' % players[select] + '   ' + link + '  ', xbmc.LOGINFO)
            PlayFromHost(link, mode='play', title=title)

        else:
            exit()
    else:
        xbmcgui.Dialog().ok('[COLOR red]Problem[/COLOR]', 'Brak linków', '')
