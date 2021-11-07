# -*- coding: utf-8 -*-

"""
    FanFilm Project
"""

import re
from urllib.parse import parse_qs, urljoin, urlencode

import requests
from ptw.libraries import cleantitle, control, client, source_utils, log_utils, apis




class source:
    def __init__(self):
        self.priority = 1
        self.language = ["pl"]
        self.session = requests.Session()
        self.tm_user = apis.tmdb_API
        self.lang = control.apiLanguage()["tmdb"]#pobrać z settings Netflixa??
        self.tmdb_by_imdb = 'https://api.themoviedb.org/3/find/%s?api_key=%s&external_source=imdb_id' % ('%s', self.tm_user)
        self.tmdb_providers = 'https://api.themoviedb.org/3/movie/%s/watch/providers?api_key=%s' % ('%s', self.tm_user)
        self.domains = ["iwaatch.com"]
        self.base_link = "https://iwaatch.com"
        self.search_link = "/?q=%s"


    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            url = {"imdb": imdb, "title": title, "year": year}

            try:
                r1 = self.tmdb_by_imdb % imdb
                result = self.session.get(r1, timeout=16).json()
                id = result['movie_results'][0]
                tmdb = id['id']
                if not tmdb:
                    return
                else:
                    tmdb = str(tmdb)
            except:
                pass
            try:
                r3 = self.session.get(self.tmdb_providers % tmdb, timeout=10)
                r3.raise_for_status()
                r3.encoding = 'utf-8'
                provider = r3.json()

                providerspage = provider['results'][self.lang.upper()]['link']
                providers_list = [i['provider_name'] for i in provider['results'][self.lang.upper()]['flatrate'] if 'Netflix' in i['provider_name']]
                url.update({'providerlink': providerspage, 'provider_list': providers_list[0]})


            except:
                pass

            url = urlencode(url)
            return url
        except:
            log_utils.log("netflix - Exception", 'sources')
            return

    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        try:
            url = {"imdb": imdb, "tvdb": tvdb, "tvshowtitle": tvshowtitle, "year": year}
            url = urlencode(url)
            return url
        except:
            log_utils.log("netflix1 - Exception", 'sources')
            return

    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        try:
            if url is None:
                return

            url = parse_qs(url)
            url = dict([(i, url[i][0]) if url[i] else (i, "") for i in url])
            url["title"], url["premiered"], url["season"], url["episode"] = (
                title,
                premiered,
                season,
                episode,
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

            title = data["title"]
            year = data["year"]
            searchlink = data['providerlink']
            header = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"}
            r = self.session.get(searchlink, headers=header, timeout=5)
            r = client.parseDOM(r.text, 'ul', attrs={'class': "providers"})[0]
            lista = [client.parseDOM(r, 'a', ret='href'), [i[-2:] for i in re.findall('ott_filter_(.+?)">', r)]]
            link = self.session.get(lista[0][0]).url
            quality = lista[1][0].upper()
            ############



  ##############


            sources.append(
                {
                    "source": "Netflix",
                    "quality": quality,
                    "language": "pl",
                    "url": link,
                    "direct": True,
                    "debridonly": False,
                }
            )
            return sources
        except:
            log_utils.log("netflix - Exception", 'sources')
            return sources

    def resolve(self, url):


        id = url.split('/')[-1]

        url = 'plugin://plugin.video.netflix/play/movie/%s' % id
        # log_utils.log('netflix - url: ' + url)
        return url
