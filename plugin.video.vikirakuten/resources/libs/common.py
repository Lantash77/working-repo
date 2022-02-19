# -*- coding: utf-8 -*-
"""
    VIKI Rakuten® addon Add-on

"""

import os
import xbmc
import xbmcaddon
import xbmcgui
import xbmcvfs


my_addon = xbmcaddon.Addon()
my_addon_id = my_addon.getAddonInfo('id')
my_addon_name = my_addon.getAddonInfo("name")
DATA_PATH = xbmcvfs.translatePath(my_addon.getAddonInfo("profile"))# or 'D:\drop'
ADDON_PATH = my_addon.getAddonInfo('path')
MEDIA_PATH = xbmcvfs.translatePath(ADDON_PATH + "resources/media/")
SetSetting = my_addon.setSetting
GetSetting = my_addon.getSetting
addonIcon = xbmcvfs.translatePath(ADDON_PATH + "resources/")+ 'icon.png'
searchFile = os.path.join(DATA_PATH, "search.db")
srtsubs_path = xbmcvfs.translatePath('special://temp/vikirakuten.English.srt')
L = my_addon.getLocalizedString
dialog = xbmcgui.Dialog()

def idle():
    xbmc.executebuiltin("Dialog.Close(busydialog)")

def metadataClean(metadata):
    if metadata == None: return metadata
    allowed = ['genre', 'country', 'year', 'episode', 'season', 'sortepisode', 'sortseason',
               'episodeguide', 'showlink', 'top250', 'setid', 'tracknumber', 'rating',
               'userrating', 'watched', 'playcount', 'overlay', 'cast', 'castandrole',
               'director', 'mpaa', 'plot', 'plotoutline', 'title', 'originaltitle', 'sorttitle',
               'duration', 'studio', 'tagline', 'writer', 'tvshowtitle', 'premiered',
               'status', 'set', 'setoverview', 'tag', 'imdbnumber', 'code', 'aired',
               'credits', 'lastplayed', 'album', 'artist', 'votes', 'path',
               'trailer', 'dateadded', 'mediatype', 'dbid']
    return {k: v for k, v in metadata.items() if k in allowed}

def clearCacheSearch(self):
    idle()
    yes = yesnoDialog(L(32056), "", "")#"Jesteś pewien?"
    if not yes:
        return
    from resources.libs import cache

    cache.cache_clear_search()
    infoDialog(L(32057), sound=True, icon="INFO")

def infoDialog(message, heading=my_addon_name, icon="", time=3000, sound=False):
    if icon == "":
        icon = addonIcon()
    elif icon == "INFO":
        icon = xbmcgui.NOTIFICATION_INFO
    elif icon == "WARNING":
        icon = xbmcgui.NOTIFICATION_WARNING
    elif icon == "ERROR":
        icon = xbmcgui.NOTIFICATION_ERROR
    dialog.notification(heading, message, icon, time, sound=sound)


def yesnoDialog(
    line1, line2, line3, heading=my_addon_name, nolabel="", yeslabel=""
):
    if isinstance(line1, bytes):
        line1 = line1.decode("utf-8")
    if isinstance(line2, bytes):
        line2 = line2.decode("utf-8")
    if isinstance(line3, bytes):
        line3 = line3.decode("utf-8")
    return dialog.yesno(heading, line1 + "\n" + line2 + "\n" + line3, nolabel, yeslabel)


def selectDialog(list, heading=my_addon_name):
    return dialog.select(heading, list)

