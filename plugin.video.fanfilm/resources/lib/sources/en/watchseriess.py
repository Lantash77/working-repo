# -*- coding: UTF-8 -*-


"""
    FanFilm Project
"""

from urllib.parse import urljoin

from ptw.libraries import cleantitle
from ptw.libraries import client
from ptw.libraries import debrid
from ptw.libraries import log_utils
from ptw.libraries import source_utils

# from ptw.libraries import cfScraper




class source:
    def __init__(self):
        self.priority = 1
        self.language = ["en"]
        self.domains = ["watchseriess.net"]
        self.base_link = "https://watchseriess.net"
        self.tvshow_link = "/series/%s-season-%s-episode-%s"
        self.headers = {"User-Agent": client.randomagent(), "Referer": self.base_link}

    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        try:
            url = cleantitle.geturl(tvshowtitle)
            return url
        except:
            return

    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        try:
            if not url:
                return
            url = urljoin(self.base_link, self.tvshow_link % (url, season, episode))
            return url
        except:
            return

    def sources(self, url, hostDict, hostprDict):
        sources = []
        try:
            if debrid.status() is True:
                return sources
            if url == None:
                return sources
            hostDict = hostprDict + hostDict
            # r = cfScraper.get(url, headers=self.headers).text
            r = client.request(url, headers=self.headers)
            links = client.parseDOM(r, "div", attrs={"class": "anime_muti_link"})[0]
            links = client.parseDOM(links, "li")[1:]
            for link in links:
                try:
                    url = client.parseDOM(link, "a", ret="data-video")[0]
                    url = (
                        urljoin(self.base_link, url)
                        if not url.startswith("http")
                        else url
                    )
                    quality, _ = source_utils.get_release_quality(url)
                    valid, host = source_utils.is_host_valid(url, hostDict)
                    if valid:
                        sources.append(
                            {
                                "source": host,
                                "quality": quality,
                                "language": "en",
                                "url": url,
                                "direct": False,
                                "debridonly": False,
                            }
                        )
                except:
                    pass
            return sources
        except:
            log_utils.log("watchseriess_exc:", 'sources')
            return sources

    def resolve(self, url):
        return url
