# -*- coding: utf-8 -*-
"""
    Covenant Add-on
    Copyright (C) 2018 :)

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

import urllib
import requests

try:
    import urllib.parse as urllib
except:
    pass

from ptw.libraries import source_utils
from ptw.libraries import cleantitle
from ptw.libraries import client


class source:
    def __init__(self):
        self.priority = 1
        self.language = ["pl"]
        self.domains = ["cda.pl"]

        self.base_link = "https://www.cda.pl/"
        self.search_link = "video/show/%s?duration=dlugie&section=&quality=720p&section=&s=best&section="
        self.search_link_ep = "video/show/%s?duration=srednie&section=&quality=720p&section=&s=best&section="
        self.anime = False
        self.year = 0
        self.headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:95.0) Gecko/20100101 Firefox/95.0',
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/jxl,image/webp,*/*;q=0.8',
                        'Accept-Language': 'pl,en-US;q=0.7,en;q=0.3',
                        'Accept-Encoding': 'gzip, deflate, br',
                        'DNT': '1',
                        'Connection': 'keep-alive',
                        'Upgrade-Insecure-Requests': '1',
                        'Sec-Fetch-Dest': 'document',
                        'Sec-Fetch-Mode': 'navigate',
                        'Sec-Fetch-Site': 'same-origin',
                        'Sec-Fetch-User': '?1',
                        'Pragma': 'no-cache',
                        'Cache-Control': 'no-cache',
                        'TE': 'trailers',
                    }

    def contains_word(self, str_to_check, word):
        if str(word).lower() in str(str_to_check).lower():
            return True
        return False

    def contains_all_words(self, str_to_check, words):
        if self.anime:
            words_to_check = str_to_check.split(" ")
            for word in words_to_check:
                try:
                    liczba = int(word)
                    for word2 in words:
                        try:
                            liczba2 = int(word2)
                            if (
                                liczba != liczba2
                                and liczba2 != self.year
                                and liczba != self.year
                            ):
                                return False
                        except:
                            continue
                except:
                    continue
        for word in words:
            if not self.contains_word(str_to_check, word):
                return False
        return True

    def search(self, title, localtitle, year, is_movie_search):
        try:
            titles = []
            titles.append(cleantitle.normalize(cleantitle.getsearch(title)))
            titles.append(cleantitle.normalize(cleantitle.getsearch(localtitle)))
            linki = []
            session = requests.session()
            session.get('https://cda.pl')

            for title in titles:
                try:
                    url = urllib.urljoin(self.base_link, self.search_link)
                    url = url % urllib.quote(str(title).replace(" ", "_"))

                    self.headers.update({'Referer': url})

                    result = session.get(url, headers=self.headers).text

                    # NB. Original query string below. It seems impossible to parse and
                    # reproduce query strings 100% accurately so the one below is given
                    # in case the reproduced version is not "correct".
                    # response = requests.get('https://www.cda.pl/video/show/w%C5%82adca_pier%C5%9Bcieni?duration=srednie&section=&quality=720p&section=&s=best&section=', headers=headers, cookies=cookies)
                    result = client.parseDOM(
                        result, "div", attrs={"class": "video-clip-wrapper"}
                    )
                except:
                    continue
                for item in result:
                    try:
                        link = str(client.parseDOM(item, "a", ret="href")[0])
                        nazwa = str(
                            client.parseDOM(
                                item, "a", attrs={"class": "link-title-visit"}
                            )[0]
                        )
                        name = cleantitle.normalize(cleantitle.getsearch(nazwa))
                        name = name.replace("  ", " ")
                        title = title.replace("  ", " ")
                        words = title.split(" ")
                        if self.contains_all_words(name, words) and str(year) in name:
                            linki.append(link)
                    except:
                        continue
            return linki
        except Exception as e:
            print(e)
            return

    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        return (tvshowtitle, localtvshowtitle), year

    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        anime = source_utils.is_anime("show", "tvdb", tvdb)
        self.year = int(url[1])
        self.anime = anime
        if anime:
            epNo = " " + source_utils.absoluteNumber(tvdb, episode, season)
        else:
            epNo = " s" + season.zfill(2) + "e" + episode.zfill(2)
        return self.search_ep(url[0][0] + epNo, url[0][1] + epNo)

    def search_ep(self, title1, title2):
        try:
            titles = []
            titles.append(cleantitle.normalize(cleantitle.getsearch(title1)))
            titles.append(cleantitle.normalize(cleantitle.getsearch(title2)))
            linki = []

            session = requests.session()
            session.get('https://cda.pl')

            for title in titles:
                try:
                    url = urllib.urljoin(self.base_link, self.search_link_ep)
                    url = url % urllib.quote(str(title).replace(" ", "_"))

                    self.headers.update({'Referer': url})

                    result = session.get(url, headers=self.headers).text

                    result = client.parseDOM(
                        result, "div", attrs={"class": "video-clip-wrapper"}
                    )
                except:
                    continue
                for item in result:
                    try:
                        link = str(client.parseDOM(item, "a", ret="href")[0])
                        nazwa = str(
                            client.parseDOM(
                                item, "a", attrs={"class": "link-title-visit"}
                            )[0]
                        )
                        name = cleantitle.normalize(cleantitle.getsearch(nazwa))
                        name = name.replace("  ", " ")
                        title = title.replace("  ", " ")
                        words = title.split(" ")
                        if self.contains_all_words(name, words):
                            linki.append(link)
                    except:
                        continue
            return linki
        except Exception as e:
            print(e)
            return

    def movie(self, imdb, title, localtitle, aliases, year):
        return self.search(title, localtitle, year, True)

    def sources(self, linki, hostDict, hostprDict):
        sources = []
        try:
            for url in linki:
                try:
                    if url == None:
                        return sources
                    url = urllib.urljoin(self.base_link, url)
                    result = client.request(url)
                    result2 = client.request("https://ebd.cda.pl/647x500/" + url.split("/")[-1] + "/vfilm")
                    title = client.parseDOM(
                        result, "span", attrs={"style": "margin-right: 3px;"}
                    )[0]
                    lang, info = self.get_lang_by_type(title)
                    valid, host = source_utils.is_host_valid(url, hostDict)
                    if not valid:
                        continue
                    if "1080p" in result2:
                        sources.append(
                            {
                                "source": host,
                                "quality": "1080p",
                                "language": lang,
                                "url": url + "?wersja=1080p",
                                "info": info,
                                "direct": False,
                                "debridonly": False,
                            }
                        )
                    if "720p" in result2:
                        sources.append(
                            {
                                "source": host,
                                "quality": "HD",
                                "language": lang,
                                "url": url + "?wersja=720p",
                                "info": info,
                                "direct": False,
                                "debridonly": False,
                            }
                        )
                    if "480p" in result2:
                        sources.append(
                            {
                                "source": host,
                                "quality": "SD",
                                "language": lang,
                                "url": url + "?wersja=480p",
                                "info": info,
                                "direct": False,
                                "debridonly": False,
                            }
                        )
                except:
                    continue
            return sources
        except Exception as e:
            print(e)
            return sources

    def get_lang_by_type(self, lang_type):
        if "dubbing" in lang_type.lower():
            if "kino" in lang_type.lower():
                return "pl", "Dubbing Kino"
            return "pl", "Dubbing"
        elif "napisy pl" in lang_type.lower():
            return "pl", "Napisy"
        elif "napisy" in lang_type.lower():
            return "pl", "Napisy"
        elif "lektor pl" in lang_type.lower():
            return "pl", "Lektor"
        elif "lektor" in lang_type.lower():
            return "pl", "Lektor"
        elif "POLSKI" in lang_type.lower():
            return "pl", None
        elif "pl" in lang_type.lower():
            return "pl", None
        return "pl", None

    def resolve(self, url):
        link = str(url).replace("//", "/").replace(":/", "://").split("?")[0]
        return str(link)
