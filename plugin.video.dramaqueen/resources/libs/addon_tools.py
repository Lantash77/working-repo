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
    try:
        if 'dqplayer' in url:
            proxyport = Getsetting('proxyport')
            videolink = url.split('|')[1]

            strmUrl, stream_header, ping = dqplayer.fetch(videolink)

            stream_header = urlencode(stream_header)
            SetSetting('hdk', str(stream_header))
            SetSetting('ping', ping)

            PROTOCOL = 'hls'
            DRM = 'com.widevine.alpha'
            import ssl
            try:
                _create_unverified_https_context = ssl._create_unverified_context
            except AttributeError:
                pass
            else:
                ssl._create_default_https_context = _create_unverified_https_context
            certificate_data = "MIIGRzCCBS+gAwIBAgISAxB1KydjidPydZjMwHQeGT0pMA0GCSqGSIb3DQEBCwUA MDIxCzAJBgNVBAYTAlVTMRYwFAYDVQQKEw1MZXQncyBFbmNyeXB0MQswCQYDVQQD EwJSMzAeFw0yMjAxMDUyMzIzMDdaFw0yMjA0MDUyMzIzMDZaMBgxFjAUBgNVBAMT DWRyYW1hcXVlZW4ucGwwggIiMA0GCSqGSIb3DQEBAQUAA4ICDwAwggIKAoICAQC0 haEudXeZPHW6W9h1nRf6gdDsrKTNuS+TpyDhDPd/yEj7KgVF3yuHIUSWqmBNyBUn V3jOIHJygh+Ad0i6BJJYEbNcGADOIl7mzQ4lch+J/jMLdE3sI3WEHU+w8wQAA6Fq Q4Vl/dIdWljd4qoeyCO4FRcBRtxFvUh3sJyWsAo5AMDr6Hkqev2HSvgRG6tzXsEi mhRhBx1AMwbeLXRNEp65E9cz5z4680WgqdXjD47UU6UVUkyyJfyLl33pkklsO3qK ANIDZDPSuVPkoMQGLisULHtfzlBL2JdTjTbmvxOYMdI6AQPJ/fVpSqmeoO0UTozX Ocgxv8lFcahKjcVI0yt6jekDIGmXCnOiCpmfDsQrNlLth9qdzLfxmKUx9nH/x0st 36G/2224g2Vafsb0zWD/iFsoDz8Pq1CiRGF0QbaC2cD4g96g6y+ygJ8b7hp1q2Zm kj9HdWN32/zu4tQK2wjfvK8Pv74UeMtC3QDnhL5apJ3sB6tJ/Ta6cg531pHWdMt3 TZ8SFm35CSOujFBYSP/0f+mNRac8XuQt1mZMzUISVJdVBzsCHyd0E+MKhgrQivVn Co0iEI04NFaKZ9N2EU4YJrnYoXGS9tkDirM3zvOwRFYjWt6NZrx1x9OkG0JKc093 YadW8jmElv+DE/TOpWdpORhp5CGItRoGau8tZBZpyQIDAQABo4ICbzCCAmswDgYD VR0PAQH/BAQDAgWgMB0GA1UdJQQWMBQGCCsGAQUFBwMBBggrBgEFBQcDAjAMBgNV HRMBAf8EAjAAMB0GA1UdDgQWBBQ1EMS3rHHYpH5Wti1GpzHDzqZZ/jAfBgNVHSME GDAWgBQULrMXt1hWy65QCUDmH6+dixTCxjBVBggrBgEFBQcBAQRJMEcwIQYIKwYB BQUHMAGGFWh0dHA6Ly9yMy5vLmxlbmNyLm9yZzAiBggrBgEFBQcwAoYWaHR0cDov L3IzLmkubGVuY3Iub3JnLzA/BgNVHREEODA2gg1kcmFtYXF1ZWVuLnBsghJtYWls LmRyYW1hcXVlZW4ucGyCEXd3dy5kcmFtYXF1ZWVuLnBsMEwGA1UdIARFMEMwCAYG Z4EMAQIBMDcGCysGAQQBgt8TAQEBMCgwJgYIKwYBBQUHAgEWGmh0dHA6Ly9jcHMu bGV0c2VuY3J5cHQub3JnMIIBBAYKKwYBBAHWeQIEAgSB9QSB8gDwAHcA36Veq2iC Tx9sre64X04+WurNohKkal6OOxLAIERcKnMAAAF+LMSToQAABAMASDBGAiEAz+BD JfpXUOAfH4UZujynOoeNc4E8zjNnQ2TgGsScRrwCIQDK597ofRREPryEejzG3q3O oNEtj76tC5j/tvdmcq4rNgB1AEalVet1+pEgMLWiiWn0830RLEF0vv1JuIWr8vxw /m1HAAABfizEk8gAAAQDAEYwRAIgLBk922vcN0CcGmRu0hTvmRH76XFPAFiu3PKI tQ3K03QCIEvxXnA7YP+tOuatRRYRIzGi9suZVMEiS5RY5tzUuA1dMA0GCSqGSIb3 DQEBCwUAA4IBAQCbcouu0alexhz4sFYkDE2do1qrSPYM8R7FE9DwCqQzdS9TaoCX gj7UdO3sUzMfRxGgWfOPwQ13RAcOCGSnExL08Ey948T0HVLgyuAErjEMtq6Fz9EZ ak6741VOFPkDci2uNrMxQRsnihPnfyPKceQv5oe9E8/QHaIP9QkNzSNAxRe/1COC wRw1P1+ZPcUgq7MlVHZcdJu0wdJ1I+6yYCeviFPTo7xAnjk6SuSS2HkVOU9Ouoge uXlB0S3WPzMvjtjcAmwCWHGvckSrN1rWNt/TzuaVhKYmtifw9YKe+Rzxa9bbshOG VsLobiUUxUx2s1Y//+knyk7clpgw7dzQJd+q"

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
                play_item.setProperty('inputstream.adaptive.server_certificate', certificate_data)
                play_item.setProperty('IsPlayable', 'true')

                xbmcplugin.setResolvedUrl(handle=int(sys.argv[1]), succeeded=True, listitem=play_item)

                # Send to resolver
        else:
            import resolveurl
            try:
                stream_url = resolveurl.resolve(url)
                xbmc.log('DramaQueen.pl | wynik z resolve  : %s' % stream_url, xbmc.LOGINFO)
                if mode == 'play':
                    li = xbmcgui.ListItem(title, path=str(stream_url))
                    xbmcplugin.setResolvedUrl(handle=int(sys.argv[1]), succeeded=True, listitem=li)
                elif mode == 'download':
                    from resources.libs import downloader
                    dest = Getsetting("download.path")
                    downloader.download(title, 'image', stream_url, dest, subdir)
            except:
                exit()

    except:
        d = xbmcgui.Dialog()
        d.notification('dramaqueen.pl ',
                       '[COLOR red]Problem  -  Nie można wyciągnąć linku[/COLOR]',
                       xbmcgui.NOTIFICATION_INFO, 5000)


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
