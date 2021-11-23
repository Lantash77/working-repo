# -*- coding: utf-8 -*-

"""
    FanFilm Project
"""

import re
from urllib.parse import parse_qs, urljoin, urlencode, quote_plus, unquote

import requests
import os
import re
from ptw.libraries import cleantitle, control, client, source_utils, log_utils




class source:
    def __init__(self):
        self.priority = 1
        self.language = ["pl"]
        self.ext = ["mp4", "mkv", "flv", "avi", "mpg"]
        self.movie_path = control.setting("movie.download.path")
        self.tv_path = control.setting("tv.download.path")
        
        
    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            title = re.sub(' ', '', title)
            title += " (%s)" % year
            transname = re.sub(r"/|:|\*|\?|\"|<|>|\+|,|\.|", "", cleantitle.normalize(title))
            dest = self.movie_path
            dest = control.transPath(dest)
            dest = os.path.join(dest, transname)            
            return urlencode(
                {
                    "imdb": imdb, 
                    "title": title,
                    "localtitle": localtitle, 
                    "year": year,
                    "path": dest,
                    "filename": transname
                }
            )
        except:
            return

    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        try:
            url = {"imdb": imdb, "tvdb": tvdb, "tvshowtitle": tvshowtitle, "year": year}
            url = urlencode(url)
            return url
        except:
            log_utils.log("pobrane - Exception", 'sources')
            return

    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        try:
            if url is None:
                return

            url = parse_qs(url)
            url = dict([(i, url[i][0]) if url[i] else (i, "") for i in url])
            
            transname = unquote(quote_plus(re.sub(r"/|:|\*|\?|\"|<|>|", "", cleantitle.normalize(url["tvshowtitle"]))))
            dest = self.tv_path
            dest = control.transPath(dest)
            dest = os.path.join(dest, transname)
            dest = os.path.join(dest, "Season %01d" % int(season))
            
            
            url["title"], url["premiered"], url["season"], url["episode"], url["path"], url["filename"] = (
                title,
                premiered,
                season,
                episode,
                dest,
                transname
            )
            url = urlencode(url)
            return url
        except:
            log_utils.log("netflix2 - Exception", 'sources')
            return

    def sources(self, url, hostDict, hostprDict):
        sources = []
        try:
            if url is None:
                return sources

            data = parse_qs(url)
            data = dict([(i, data[i][0]) if data[i] else (i, "") for i in data])
            path = data['path']
            filename = data['filename']

            if 'tvshowtitle' in data:
                filename = re.sub(r'\+', '', data['filename']) + ' S%02dE%02d' % (int(data['season']), int(data['episode']))
            else:
                filename = data['filename']
            if os.path.exists(path):
                for r, d, f in os.walk(path):
                    for file in f:
                        if filename in file:
                            if [file.endswith(ext) for ext in self.ext]:
                                url = os.path.join(r, file)
                        else:
                           return sources
            else:
                return sources
            sources.append(
                {
                    "source": "pobrane",
                    "quality": 'HD',
                    "language": "pl",
                    "url": url,
                    "direct": True,
                    "debridonly": False,
                }
            )

            return sources
        except:
            log_utils.log("pobrane - Exception", 'sources')
            return sources

    def resolve(self, url):

        return url
