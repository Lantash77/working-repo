# -*- coding: utf-8 -*-

"""
    FanFilm Add-on
    Copyright (C) 2017 homik

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

try:
    import urlparse
except:
    import urllib.parse as urlparse

import json
import requests

# from ptw.libraries import cleantitle, source_utils
# from ptw.libraries import client, cache
from ptw.libraries import cleantitle, source_utils
from ptw.libraries import client, cache


class source:
    def __init__(self):
        self.priority = 1
        self.language = ["pl"]
        self.domains = ["vizjer.pl"]

        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:75.0) Gecko/20100101 Firefox/75.0",
            ":authority": self.domains,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "pl,en-US;q=0.7,en;q=0.3",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }

        self.base_link = "http://vizjer.pl/"
        self.search_link = "/wyszukiwarka?phrase=%s"

    def contains_word(self, str_to_check, word):
        if str(word).lower() in str(str_to_check).lower():
            return True
        return False

    def contains_all_words(self, str_to_check, words):
        for word in words:
            if not self.contains_word(str_to_check, word):
                return False
        return True

    def do_search(self, title, local_title, year):
        try:
            titles = []
            titles.append(cleantitle.normalize(cleantitle.getsearch(title)))
            titles.append(cleantitle.normalize(cleantitle.getsearch(local_title)))

            for title in titles:
                try:
                    url = urlparse.urljoin(self.base_link, self.search_link)
                    url = url % urlparse.quote_plus(cleantitle.query(title))
                    data = {
                        'phrase': title
                    }
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:93.0) Gecko/20100101 Firefox/93.0',
                        'Accept': '*/*',
                        'Accept-Language': 'pl,en-US;q=0.7,en;q=0.3',
                        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                        'X-Requested-With': 'XMLHttpRequest',
                        'Origin': 'https://vizjer.pl',
                        'DNT': '1',
                        'Alt-Used': 'vizjer.pl',
                        'Connection': 'keep-alive',
                        'Referer': 'https://vizjer.pl/wyszukiwarka?phrase=' + title,
                        'Sec-Fetch-Dest': 'empty',
                        'Sec-Fetch-Mode': 'cors',
                        'Sec-Fetch-Site': 'same-origin',
                        'Pragma': 'no-cache',
                        'Cache-Control': 'no-cache',
                        'TE': 'trailers',
                    }
                    result = client.request('https://vizjer.pl/szukaj', headers=headers, post=data)
                    results = client.parseDOM(result, "div", attrs={"class": "col-xs-3 col-lg-2"})
                    for row in results:
                        name = client.parseDOM(row, "div", attrs={"class": "title"})[0]
                        rok = client.parseDOM(row, "div", attrs={"class": "year"})[0]
                        words = title.split(" ")
                        if self.contains_all_words(
                            cleantitle.normalize(cleantitle.getsearch(name)), words
                        ) and str(year) in str(rok):
                            url = client.parseDOM(row, "a", ret="href")[0]
                            return url
                except Exception as e:
                    continue
        except:
            return

    def movie(self, imdb, title, localtitle, aliases, year):
        return self.do_search(title, localtitle, year)

    def sources(self, url, hostDict, hostprDict):
        sources = []
        try:
            if url == None:
                return sources
            sources = []

            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:93.0) Gecko/20100101 Firefox/93.0',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                'Accept-Language': 'pl,en-US;q=0.7,en;q=0.3',
                'Referer': 'https://vizjer.pl/wyszukiwarka?phrase=test',
                'DNT': '1',
                'Alt-Used': 'vizjer.pl',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'same-origin',
                'Sec-Fetch-User': '?1',
                'Pragma': 'no-cache',
                'Cache-Control': 'no-cache',
            }
            result = client.request(url, headers=headers)
            result = client.parseDOM(result, "table", attrs={"class": "table table-bordered"})
            result = client.parseDOM(result, "tbody")[0]
            result = client.parseDOM(result, "tr")
            for item in result:
                try:
                    item2 = client.parseDOM(result, "td")
                    jezyk = item2[2]
                    jezyk, info = self.get_lang_by_type(jezyk)
                    quality = item2[3]
                    url = client.parseDOM(item, "a", ret="href")[0]
                    valid, host = source_utils.is_host_valid(url, hostDict)
                    if "wysoka" in quality.lower():
                        sources.append(
                            {
                                "source": host,
                                "quality": "HD",
                                "language": jezyk,
                                "url": url,
                                "info": info,
                                "direct": False,
                                "debridonly": False,
                            }
                        )
                    elif "rednia" in quality.lower():
                        sources.append(
                            {
                                "source": host,
                                "quality": "SD",
                                "language": jezyk,
                                "url": url,
                                "info": info,
                                "direct": False,
                                "debridonly": False,
                            }
                        )
                    elif "niska" in quality.lower():
                        sources.append(
                            {
                                "source": host,
                                "quality": "SD",
                                "language": jezyk,
                                "url": url,
                                "info": info,
                                "direct": False,
                                "debridonly": False,
                            }
                        )
                    else:
                        sources.append(
                            {
                                "source": host,
                                "quality": "SD",
                                "language": jezyk,
                                "url": url,
                                "info": info,
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
        elif "lektor pl" in lang_type.lower():
            return "pl", "Lektor"
        elif "lektor" in lang_type.lower():
            return "pl", "Lektor"
        elif "napisy pl" in lang_type.lower():
            return "pl", "Napisy"
        elif "napisy" in lang_type.lower():
            return "pl", "Napisy"
        elif "POLSKI" in lang_type.lower():
            return "pl", None
        elif "pl" in lang_type.lower():
            return "pl", None
        return "en", None

    def resolve(self, url):
        return url
