# -*- coding: utf-8 -*-

"""
    FanFilm Add-on
    Copyright (C) 2016 mrknow

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
import sys
from urllib.parse import parse_qsl, quote_plus
from contextlib import contextmanager

import xbmc

from ptw.libraries import control

ladowanie = control.setting("ladowanie")

params = dict(parse_qsl(sys.argv[2].replace("?", "")))

action = params.get("action")

@contextmanager
def busy_dialog():
    try:
        if ladowanie == "true" and action not in (
            "playItem",
            "service",
            "movies",
            "tvshows",
            "updateLibrary",
            "service",
        ):
            xbmc.executebuiltin("ActivateWindow(busydialognocancel)")
        yield
    finally:
        if ladowanie == "true" and action not in (
            "playItem",
            "service",
            "movies",
            "tvshows",
            "updateLibrary",
            "service",
        ):
            xbmc.executebuiltin("Dialog.Close(busydialognocancel)")


with busy_dialog():
    name = params.get("name")

    title = params.get("title")

    year = params.get("year")

    imdb = params.get("imdb")

    tvdb = params.get("tvdb")

    tmdb = params.get("tmdb")

    season = params.get("season")

    episode = params.get("episode")

    tvshowtitle = params.get("tvshowtitle")

    premiered = params.get("premiered")

    url = params.get("url")

    image = params.get("image")

    meta = params.get("meta")

    select = params.get("select")

    query = params.get("query")

    source = params.get("source")

    content = params.get("content")

    windowedtrailer = params.get("windowedtrailer")
    windowedtrailer = int(windowedtrailer) if windowedtrailer in ("0", "1") else 0

    if action == None:
        from resources.lib.indexers import navigator

        navigator.navigator().root()

    elif action == "movieNavigator":
        from resources.lib.indexers import navigator

        navigator.navigator().movies()

    elif action == "movieliteNavigator":
        from resources.lib.indexers import navigator

        navigator.navigator().movies(lite=True)

    elif action == "mymovieNavigator":
        from resources.lib.indexers import navigator

        navigator.navigator().mymovies()

    elif action == "mymovieliteNavigator":
        from resources.lib.indexers import navigator

        navigator.navigator().mymovies(lite=True)

    elif action == "tvNavigator":
        from resources.lib.indexers import navigator

        navigator.navigator().tvshows()

    elif action == "tvliteNavigator":
        from resources.lib.indexers import navigator

        navigator.navigator().tvshows(lite=True)

    elif action == "mytvNavigator":
        from resources.lib.indexers import navigator

        navigator.navigator().mytvshows()

    elif action == "mytvliteNavigator":
        from resources.lib.indexers import navigator

        navigator.navigator().mytvshows(lite=True)

    elif action == "downloadNavigator":
        from resources.lib.indexers import navigator

        navigator.navigator().downloads()

    elif action == "libraryNavigator":
        from resources.lib.indexers import navigator

        navigator.navigator().library()

    elif action == "toolNavigator":
        from resources.lib.indexers import navigator

        navigator.navigator().tools()

    elif action == "searchNavigator":
        from resources.lib.indexers import navigator

        navigator.navigator().search()

    elif action == "viewsNavigator":
        from resources.lib.indexers import navigator

        navigator.navigator().views()

    elif action == "clearCache":
        from resources.lib.indexers import navigator

        navigator.navigator().clearCache()

    elif action == "clearCacheSearch":
        from resources.lib.indexers import navigator

        navigator.navigator().clearCacheSearch()

    elif action == "infoCheck":
        from resources.lib.indexers import navigator

        navigator.navigator().infoCheck("")

    elif action == "downloadManager":
        from ptw.libraries import downloader

        try:
            downloader.downloadManager()
        except:
            pass

    elif action == "movies":
        from resources.lib.indexers import movies

        movies.movies().get(url)

    elif action == "moviePage":
        from resources.lib.indexers import movies

        movies.movies().get(url)

    elif action == "movieWidget":
        from resources.lib.indexers import movies

        movies.movies().widget()

    elif action == "movieSearch":
        from resources.lib.indexers import movies

        movies.movies().search()

    elif action == "movieSearchnew":
        from resources.lib.indexers import movies

        movies.movies().search_new()

    elif action == "movieSearchterm":
        from resources.lib.indexers import movies

        movies.movies().search_term(name)

    elif action == "moviePerson":
        from resources.lib.indexers import movies

        movies.movies().person()

    elif action == "movieGenres":
        from resources.lib.indexers import movies

        movies.movies().genres()

    elif action == "movieLanguages":
        from resources.lib.indexers import movies

        movies.movies().languages()

    elif action == "movieCertificates":
        from resources.lib.indexers import movies

        movies.movies().certifications()

    elif action == "movieYears":
        from resources.lib.indexers import movies

        movies.movies().years()

    elif action == "movieYearsTop":
        from resources.lib.indexers import movies

        movies.movies().years_top()

    elif action == "moviesAwards":
        from resources.lib.indexers import movies

        movies.movies().awards()

    elif action == "movieCompanies":
        from resources.lib.indexers import movies

        movies.movies().companies()

    elif action == "moviePersons":
        from resources.lib.indexers import movies

        movies.movies().persons(url)

    elif action == "movieUserlists":
        from resources.lib.indexers import movies

        movies.movies().userlists()

    elif action == "myimdbMovieLists":
        from resources.lib.indexers import movies

        movies.movies().my_imdbUserLists()

    elif action == "myimdbTVLists":
        from resources.lib.indexers import tvshows

        tvshows.tvshows().my_imdbUserLists()

    elif action == "channels":
        from resources.lib.indexers import channels

        channels.channels().get()

    elif action == "tvshows":
        from resources.lib.indexers import tvshows

        tvshows.tvshows().get(url)

    elif action == "tvshowPage":
        from resources.lib.indexers import tvshows

        tvshows.tvshows().get(url)

    elif action == "tvSearch":
        from resources.lib.indexers import tvshows

        tvshows.tvshows().search()

    elif action == "tvSearchnew":
        from resources.lib.indexers import tvshows

        tvshows.tvshows().search_new()

    elif action == "tvSearchterm":
        from resources.lib.indexers import tvshows

        tvshows.tvshows().search_term(name)

    elif action == "tvPerson":
        from resources.lib.indexers import tvshows

        tvshows.tvshows().person()

    elif action == "tvGenres":
        from resources.lib.indexers import tvshows

        tvshows.tvshows().genres()

    elif action == "tvNetworks":
        from resources.lib.indexers import tvshows

        tvshows.tvshows().networks()

    elif action == "tvLanguages":
        from resources.lib.indexers import tvshows

        tvshows.tvshows().languages()

    elif action == "tvCertificates":
        from resources.lib.indexers import tvshows

        tvshows.tvshows().certifications()

    elif action == "tvYearsTop":
        from resources.lib.indexers import tvshows

        tvshows.tvshows().years_top()

    elif action == "tvPersons":
        from resources.lib.indexers import tvshows

        tvshows.tvshows().persons(url)

    elif action == "tvUserlists":
        from resources.lib.indexers import tvshows

        tvshows.tvshows().userlists()

    elif action == "seasons":
        from resources.lib.indexers import episodes

        episodes.seasons().get(tvshowtitle, year, imdb, tmdb, meta)

    elif action == "episodes":
        from resources.lib.indexers import episodes

        episodes.episodes().get(tvshowtitle, year, imdb, tmdb, meta, season, episode)

    elif action == "calendar":
        from resources.lib.indexers import episodes

        episodes.episodes().calendar(url)

    elif action == "tvWidget":
        from resources.lib.indexers import episodes

        episodes.episodes().widget()

    elif action == "calendars":
        from resources.lib.indexers import episodes

        episodes.episodes().calendars()

    elif action == "episodeUserlists":
        from resources.lib.indexers import episodes

        episodes.episodes().userlists()

    elif action == "refresh":
        from ptw.libraries import control

        control.refresh()

    elif action == "queueItem":
        from ptw.libraries import control

        control.queueItem()

    elif action == "openSettings":
        from ptw.libraries import control

        control.openSettings(query)

    elif action == "artwork":
        from ptw.libraries import control

        control.artwork()

    elif action == "addView":
        from ptw.libraries import views

        views.addView(content)

    elif action == "moviePlaycount":
        from ptw.libraries import playcount

        playcount.movies(imdb, query)

    elif action == "episodePlaycount":
        from ptw.libraries import playcount

        playcount.episodes(imdb, tvdb, season, episode, query)

    elif action == "tvPlaycount":
        from ptw.libraries import playcount

        playcount.tvshows(name, imdb, tmdb, season, query)

    elif action == "trailer":
        Zamknij = False
        from ptw.libraries import trailer

        trailer.trailer().play(name, url, windowedtrailer)

    elif action == "traktManager":
        from ptw.libraries import trakt

        trakt.manager(name, imdb, tmdb, content)

    elif action == "authTrakt":
        from ptw.libraries import trakt

        trakt.authTrakt()

    elif action == "smuSettings":
        try:
            import resolveurl
        except:
            pass
        resolveurl.display_settings()

    elif action == "download":
        import json
        from ptw.libraries import sources
        from ptw.libraries import downloader

        try:
            Zamknij = False
            downloader.download(
                name,
                image,
                sources.sources().sourcesResolve(json.loads(source)[0], True),
            )
        except Exception as e:
            pass

    elif action == "play":
        from ptw.libraries import sources

        sources.sources().play(
            title,
            year,
            imdb,
            tmdb,
            season,
            episode,
            tvshowtitle,
            premiered,
            meta,
            select,
        )

    elif action == "addItem":
        from ptw.libraries import sources

        sources.sources().addItem(title)

    elif action == "playItem":
        from ptw.libraries import sources

        sources.sources().playItem(title, source)

    elif action == "alterSources":
        from ptw.libraries import sources

        sources.sources().alterSources(url, meta)

    elif action == "clearSources":
        from ptw.libraries import sources

        sources.sources().clearSources()

    elif action == "random":
        rtype = params.get("rtype")
        if rtype == "movie":
            from resources.lib.indexers import movies

            rlist = movies.movies().get(url, create_directory=False)
            r = sys.argv[0] + "?action=play"
        elif rtype == "episode":
            from resources.lib.indexers import episodes

            rlist = episodes.episodes().get(
                tvshowtitle, year, imdb, tmdb, season, create_directory=False
            )
            r = sys.argv[0] + "?action=play"
        elif rtype == "season":
            from resources.lib.indexers import episodes

            rlist = episodes.seasons().get(
                tvshowtitle, year, imdb, tmdb, create_directory=False
            )
            r = sys.argv[0] + "?action=random&rtype=episode"
        elif rtype == "show":
            from resources.lib.indexers import tvshows

            rlist = tvshows.tvshows().get(url, create_directory=False)
            r = sys.argv[0] + "?action=random&rtype=season"
        from ptw.libraries import control
        from random import randint
        import json

        try:
            rand = randint(1, len(rlist)) - 1
            for p in [
                "title",
                "year",
                "imdb",
                "tmdb",
                "season",
                "episode",
                "tvshowtitle",
                "premiered",
                "select",
            ]:
                if rtype == "show" and p == "tvshowtitle":
                    try:
                        r += "&" + p + "=" + quote_plus(rlist[rand]["title"])
                    except:
                        pass
                else:
                    try:
                        r += "&" + p + "=" + quote_plus(rlist[rand][p])
                    except:
                        pass
            try:
                r += "&meta=" + quote_plus(json.dumps(rlist[rand]))
            except:
                r += "&meta=" + quote_plus("{}")
            if rtype == "movie":
                try:
                    control.infoDialog(
                        rlist[rand]["title"],
                        control.lang(32536).encode("utf-8"),
                        time=30000,
                    )
                except:
                    pass
            elif rtype == "episode":
                try:
                    control.infoDialog(
                        rlist[rand]["tvshowtitle"]
                        + " - Season "
                        + rlist[rand]["season"]
                        + " - "
                        + rlist[rand]["title"],
                        control.lang(32536).encode("utf-8"),
                        time=30000,
                    )
                except:
                    pass
            control.execute("RunPlugin(%s)" % r)
        except:
            control.infoDialog(control.lang(32537).encode("utf-8"), time=8000)

    elif action == "movieToLibrary":
        from ptw.libraries import libtools

        libtools.libmovies().add(name, title, year, imdb, tmdb)

    elif action == "moviesToLibrary":
        from ptw.libraries import libtools

        libtools.libmovies().range(url)

    elif action == "moviesToLibrarySilent":
        from ptw.libraries import libtools

        libtools.libmovies().silent(url)

    elif action == "tvshowToLibrary":
        from ptw.libraries import libtools

        libtools.libtvshows().add(tvshowtitle, year, imdb, tvdb)

    elif action == "tvshowsToLibrary":
        from ptw.libraries import libtools

        libtools.libtvshows().range(url)

    elif action == "tvshowsToLibrarySilent":
        from ptw.libraries import libtools

        libtools.libtvshows().silent(url)

    elif action == "updateLibrary":
        from ptw.libraries import libtools

        libtools.libepisodes().update(query)

    elif action == "service":
        from ptw.libraries import libtools

        libtools.libepisodes().service()
