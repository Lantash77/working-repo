# -*- coding: UTF-8 -*-
import sys
import re
import urllib.request, urllib.parse, urllib.error
from urllib.parse import parse_qs, quote_plus, urlencode, unquote
from resources.libs import dqplayer
import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon
import inputstreamhelper

from resources.libs import cache


my_addon = xbmcaddon.Addon()
Getsetting = my_addon.getSetting
SetSetting = my_addon.setSetting


def addDir(name, url, mode='', icon='', thumb='', fanart='', poster='', banner='', clearart='', clearlogo='',
           genre='', year='', rating='', dateadded='', plot='', subdir='',
           section='', page='', code='', studio='', meta='',
           isFolder=True, total=1):
    u = (sys.argv[0] + '?url=' + quote_plus(url) + '&mode=' + str(mode) + '&name='
         + quote_plus(name) + '&img=' + quote_plus(thumb)
         + '&section=' + quote_plus(section) + '&page=' + quote_plus(page)
         + '&subdir=' + quote_plus(subdir))
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
            banner='', clearart='', clearlogo='', genre='', year='', subdir='',
            rating='', dateadded='', plot='', code='', studio='', meta='',
            isFolder=False, total=1,
            type='video', section='', page=''):
    u = (sys.argv[0] + '?url=' + quote_plus(url) + '&mode=' + str(mode)
         + '&name=' + quote_plus(name) + '&img=' + quote_plus(thumb)
         + '&section=' + quote_plus(section) + '&page=' + quote_plus(page)
         + '&subdir=' + quote_plus(subdir))
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

def PlayFromHost(url, mode, title, subdir=''):
    try:
        from urllib.parse import urlencode, quote_plus, quote, unquote
    except ImportError:
        from urllib import urlencode, quote_plus, quote, unquote

    if 'google' in url:
        url = url.replace('preview', 'view')

    #DQ Player
    if 'dqplayer' in url:
        proxyport = Getsetting('proxyport')
        videolink = url.split('|')[1]

        strmUrl, stream_header = dqplayer.fetch(videolink)

        stream_header = urlencode(stream_header)
        SetSetting('hdk', str(stream_header))

        PROTOCOL = 'hls'
        DRM = 'com.widevine.alpha'

        import inputstreamhelper

        is_helper = inputstreamhelper.Helper(PROTOCOL)

        prxy ='http://127.0.0.1:%s/tqdrama='%(str(proxyport))
        strmUrl = prxy+strmUrl

        if is_helper.check_inputstream():
            play_item = xbmcgui.ListItem(path=strmUrl)

            play_item.setMimeType('application/x-mpegURL')
            play_item.setContentLookup(False)
            play_item.setProperty('inputstream', is_helper.inputstream_addon)
            play_item.setProperty('inputstream.adaptive.manifest_type', 'hls')
            play_item.setProperty('inputstream.adaptive.stream_headers', stream_header)
            play_item.setProperty('IsPlayable', 'true')

            xbmcplugin.setResolvedUrl(handle=int(sys.argv[1]), succeeded=True, listitem=play_item)

def SourceSelect(players, links, title, subdir=''):

    if len(players) > 0:
        d = xbmcgui.Dialog()
        select = d.select('Wybór playera', players)
        if select > -1:
            link = str(links[select])
            xbmc.log('DramaQueen.pl | Proba z : %s' % players[select] + '   ' + link + '  ', xbmc.LOGINFO)
            if Getsetting('download.opt') == 'true':
                ret = d.yesno('Pobieranie', 'Wybierz Opcję', 'Oglądaj', 'Pobierz')
                if ret:
                    mode = 'download'
                else:
                    mode = 'play'
            else:
                mode = 'play'
            PlayFromHost(link, mode='play', title=title, subdir=subdir)

        else:
            exit()
    else:
        xbmcgui.Dialog().ok('[COLOR red]Problem[/COLOR]', 'Brak linków', '')
