# -*- coding: utf-8 -*-
"""
    FanFilm Add-on
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

from ptw.libraries import cleantitle, source_utils
from ptw.libraries import client


class source:
    def __init__(self):
        self.priority = 1
        self.language = ["pl"]
        self.domains = ["zaluknij.xyz"]

        self.base_link = "http://zaluknij.xyz/"
        self.search_link = "http://zaluknij.xyz/?s=%s"
        self.anime = False
        self.year = 0

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
            titles = [
                cleantitle.normalize(cleantitle.getsearch(title)),
                cleantitle.normalize(cleantitle.getsearch(localtitle)),
            ]
            linki = []
            for title in titles:
                try:
                    url = self.search_link % urllib.quote(str(title).replace(" ", "+"))
                    result = client.request(url)
                    result = client.parseDOM(
                        result, "div", attrs={"class": "result-item"}
                    )
                except:
                    continue
                for item in result:
                    try:
                        link = client.parseDOM(item, "a", ret="href")[0]
                        nazwa = client.parseDOM(item, "img", ret="alt")[0]
                        rok = client.parseDOM(result, "span", attrs={"class": "year"})[
                            0
                        ]
                        name = cleantitle.normalize(cleantitle.getsearch(nazwa))
                        name = name.replace("  ", " ")
                        title = title.replace("  ", " ")
                        words = title.split(" ")
                        if self.contains_all_words(name, words) and str(year) in rok:
                            return link
                    except:
                        continue
            return linki
        except Exception as e:
            print(e)
            return

    def fix_game_of_thrones(self, title, year):
        if title == "Gra o tron" or title == "Game of Thrones":
            return "2011"
        else:
            return year

    def search_ep(self, titles, season, episode):
        try:
            for title in titles[0]:
                try:
                    year = self.fix_game_of_thrones(title, titles[1])
                    url = self.search_link % urllib.quote(str(title).replace(" ", "+"))
                    result = client.request(url)
                    result = client.parseDOM(
                        result, "div", attrs={"class": "result-item"}
                    )
                except:
                    continue
                for item in result:
                    try:
                        link = client.parseDOM(item, "a", ret="href")[0]
                        nazwa = client.parseDOM(item, "img", ret="alt")[0]
                        rok = client.parseDOM(result, "span", attrs={"class": "year"})[
                            0
                        ]
                        name = cleantitle.normalize(cleantitle.getsearch(nazwa))
                        name = name.replace("  ", " ")
                        title = title.replace("  ", " ")
                        words = title.split(" ")
                        if self.contains_all_words(name, words) and str(year) in rok:
                            link = link.replace("/tvshows/", "/episodes/")[
                                :-1
                            ] + "-%sx%s" % (season, episode)
                            return link
                    except:
                        continue
            return None
        except Exception as e:
            print(e)
            return

    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        return (tvshowtitle, localtvshowtitle), year

    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        return self.search_ep(url, season, episode)

    def movie(self, imdb, title, localtitle, aliases, year):
        return self.search(title, localtitle, year, True)

    def sources(self, url, hostDict, hostprDict):
        sources = []
        try:
            result = client.request(url)
            result = client.parseDOM(result, "div", attrs={"class": "fix-table"})
            result = client.parseDOM(result, "tbody")
            result = client.parseDOM(result, "tr")
            for item in result:
                try:
                    # quality = client.parseDOM(item, 'strong')[0]
                    video_link = client.parseDOM(item, "a", ret="href")[0]
                    video_link = requests.get(
                        video_link, allow_redirects=False
                    ).headers["location"]
                    opis = client.parseDOM(item, "td")[2]
                    lang, opis = self.get_lang_by_type(opis)
                    quality = source_utils.check_sd_url(video_link)
                    valid, host = source_utils.is_host_valid(video_link, hostDict)
                    sources.append(
                        {
                            "source": host,
                            "quality": quality,
                            "language": lang,
                            "url": video_link,
                            "info": opis,
                            "direct": False,
                            "debridonly": False,
                        }
                    )
                except:
                    continue
            return sources
        except:
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
        return url