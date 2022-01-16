# -*- coding: utf-8 -*-

'''
    FanFilm Add-on  2021
    Źródło w fazie testów
'''

import re
import requests
from urllib.parse import parse_qs, urlencode

from ptw.libraries import cleantitle, control, log_utils, apis
from resources.lib.indexers.justwatch import JustWatch

netflix_plugin = 'plugin.video.netflix'
prime_plugin = 'plugin.video.amazon-test'
hbogo_plugin = 'plugin.video.hbogoeu'
hbomax_plugin = 'slyguy.hbo.max'
disney_plugin = 'slyguy.disney.plus'
iplayer_plugin = 'plugin.video.iplayerwww'
curstream_plugin = 'slyguy.curiositystream'
hulu_plugin = 'slyguy.hulu'
paramount_plugin = 'slyguy.paramount.plus'

netflix_enabled = control.condVisibility('System.HasAddon(%s)' % netflix_plugin)
prime_enabled = control.condVisibility('System.HasAddon(%s)' % prime_plugin)
hbogo_enabled = control.condVisibility('System.HasAddon(%s)' % hbogo_plugin)
hbomax_enabled = control.condVisibility('System.HasAddon(%s)' % hbomax_plugin)
disney_enabled = control.condVisibility('System.HasAddon(%s)' % disney_plugin)
iplayer_enabled = control.condVisibility('System.HasAddon(%s)' % iplayer_plugin)
curstream_enabled = control.condVisibility('System.HasAddon(%s)' % curstream_plugin)
hulu_enabled = control.condVisibility('System.HasAddon(%s)' % hulu_plugin)
paramount_enabled = control.condVisibility('System.HasAddon(%s)' % paramount_plugin)

netflix_pattern = 'plugin://plugin.video.netflix/play/movie/%s'
prime_pattern = 'plugin://plugin.video.amazon-test/?asin=%s&mode=PlayVideo&name=None&adult=0&trailer=0&selbitrate=0'
hbogo_pattern = ''#  do zrobienia
hbomax_pattern = 'plugin://slyguy.hbo.max/?_=play&slug='
disney_pattern = 'plugin://slyguy.disney.plus/?_=play&_play=1&content_id='
iplayer_pattern = 'plugin://plugin.video.iplayerwww/?url=%s&mode=202&name=null&iconimage=null&description=null&subtitles_url=&logged_in=False'
curstream_pattern = 'plugin://slyguy.curiositystream/?_=play&_play=1&id='
hulu_pattern = 'plugin://slyguy.hulu/?_=play&id='
paramount_pattern = 'plugin://slyguy.paramount.plus/?_=play&id='

scraper_init = any(e for e in [netflix_enabled,
                               prime_enabled,
                               hbomax_enabled,
                               disney_enabled,
                               iplayer_enabled,
                               curstream_enabled,
                               hulu_enabled,
                               paramount_enabled]
                   )

class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en', 'el']
        self.domains = []
        self.base_link = ''
        self.session = requests.Session()
        self.tm_user = apis.tmdb_API
        self.country = control.setting('external.country') or 'US'
        self.tm_user = control.setting('tm.user') or apis.tmdb_key
        self.tmdb_by_imdb = 'https://api.themoviedb.org/3/find/%s?api_key=%s&external_source=imdb_id' % ('%s', self.tm_user)
        self.aliases = []

    def movie(self, imdb, title, localtitle, aliases, year):
        if not scraper_init:
            return

        try:
            self.aliases.extend(aliases)
            url = {'imdb': imdb, 'title': title, 'year': year}
            url = urlencode(url)
            return url
        except:
            return

    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        if not scraper_init:
            return

        try:
            self.aliases.extend(aliases)
            url = {'imdb': imdb, 'tvdb': tvdb, 'tvshowtitle': tvshowtitle, 'year': year}
            url = urlencode(url)
            return url
        except Exception:
            return

    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        try:
            if url is None: return
            url = parse_qs(url)
            url = dict([(i, url[i][0]) if url[i] else (i, '') for i in url])
            url['title'], url['premiered'], url['season'], url['episode'] = title, premiered, season, episode
            url = urlencode(url)
            return url
        except Exception:
            return

    def sources(self, url, hostDict, hostprDict):
        sources = []
        try:
            if url is None: return sources

            data = parse_qs(url)
            data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])
            title = data['tvshowtitle'] if 'tvshowtitle' in data else data['title']
            year = data['year']
            content = 'movie' if not 'tvshowtitle' in data else 'show'

            result = None

            jw = JustWatch(country=self.country)
            # r0 = jw.get_providers()
            # log_utils.log('justwatch {0} providers: {1}'.format(self.country, repr(r0)))

            if content == 'movie':
                tmdb = requests.get(self.tmdb_by_imdb % data['imdb']).json()
                tmdb = tmdb['movie_results'][0]['id']

                r = jw.search_for_item(query=title.lower())
                items = r['items']

                for item in items:
                    tmdb_id = item['scoring']
                    if tmdb_id:
                        tmdb_id = [t['value'] for t in tmdb_id if t['provider_type'] == 'tmdb:id']
                        if tmdb_id:
                            if tmdb_id[0] == tmdb:
                                result = item
                                break

            else:
                jw0 = JustWatch(country='US')
                r = jw0.search_for_item(query=title.lower())

                items = r['items']
                jw_id = [i for i in items if self.is_match(' '.join((i['title'], str(i['original_release_year']))), title, year, self.aliases)]
                jw_id = [i['id'] for i in jw_id if i['object_type'] == 'show']
                if jw_id:
                    r = jw.get_episodes(str(jw_id[0]))
                    item = r['items']
                    item = [i for i in item if i['season_number'] == int(data['season']) and i['episode_number'] == int(data['episode'])]
                    if not item:
                        r = jw.get_episodes(str(jw_id[0]), page='2')
                        item = r['items']
                        item = [i for i in item if i['season_number'] == int(data['season']) and i['episode_number'] == int(data['episode'])]
                    if item:
                        result = item[0]

            if not result:
                raise Exception('%s not found in jw database' % title)
            #log_utils.log('justwatch result: ' + repr(result))

            offers = result.get('offers')
            if not offers:
                raise Exception('%s not available in %s' % (title, self.country))
            #log_utils.log('justwatch offers: ' + repr(offers))

            netflix = ['nfx', 'nfk']
            prime = ['amp', 'prv', 'aim']
            hbo = ['hmf', 'hbm', 'hbo', 'hbn']
            disney = ['dnp']
            iplayer = ['bbc']
            curstream = ['cts']
            hulu = ['hlu']
            paramount = ['pmp']

            streams = []

            if netflix_enabled:
                nfx = [o for o in offers if o['package_short_name'] in netflix]
                if nfx:
                    nfx_id = nfx[0]['urls']['standard_web']
                    nfx_id = nfx_id.rstrip('/').split('/')[-1]
                    if content == 'movie':
                        netflix_id = nfx_id
                    else:
                        netflix_id = self.netflix_ep_id(nfx_id, data['season'], data['episode'])
                    if netflix_id:
                        #log_utils.log('official netflix_id: ' + netflix_id)
                        streams.append(('netflix', netflix_pattern % netflix_id))

            if prime_enabled:
                prv = [o for o in offers if o['package_short_name'] in prime]
                if prv:
                    prime_id = prv[0]['urls']['standard_web']
                    prime_id = prime_id.rstrip('/').split('gti=')[1]
                    #log_utils.log('official prime_id: ' + prime_id)
                    streams.append(('amazon prime', prime_pattern % prime_id))

            if hbomax_enabled:
                hbm = [o for o in offers if o['package_short_name'] in hbo]
                if hbm:
                    hbo_id = hbm[0]['urls']['standard_web']
                    hbo_id = hbo_id.rstrip('/').split('/')[-1]
                    #log_utils.log('official hbo_id: ' + hbo_id)
                    streams.append(('hbo max', hbomax_pattern + hbo_id))

            if disney_enabled:
                dnp = [o for o in offers if o['package_short_name'] in disney]
                if dnp:
                    disney_id = dnp[0]['urls']['deeplink_web']
                    disney_id = disney_id.rstrip('/').split('/')[-1]
                    #log_utils.log('official disney_id: ' + disney_id)
                    streams.append(('disney+', disney_pattern + disney_id))

            if iplayer_enabled:
                bbc = [o for o in offers if o['package_short_name'] in iplayer]
                if bbc:
                    iplayer_id = bbc[0]['urls']['standard_web']
                    #log_utils.log('official iplayer_id: ' + iplayer_id)
                    streams.append(('bbc iplayer', iplayer_pattern % iplayer_id))

            if curstream_enabled:
                cts = [o for o in offers if o['package_short_name'] in curstream]
                if cts:
                    cts_id = cts[0]['urls']['standard_web']
                    cts_id = cts_id.rstrip('/').split('/')[-1]
                    #log_utils.log('official cts_id: ' + cts_id)
                    streams.append(('curiosity stream', curstream_pattern + cts_id))

            if hulu_enabled:
                hlu = [o for o in offers if o['package_short_name'] in hulu]
                if hlu:
                    hulu_id = hlu[0]['urls']['standard_web']
                    hulu_id = hulu_id.rstrip('/').split('/')[-1]
                    #log_utils.log('official hulu_id: ' + hulu_id)
                    streams.append(('hulu', hulu_pattern + hulu_id))

            if paramount_enabled:
                pmp = [o for o in offers if o['package_short_name'] in paramount]
                if pmp:
                    pmp_url = pmp[0]['urls']['standard_web']
                    pmp_id = pmp_url.split('?')[0].split('/')[-1] if content == 'movie' else re.findall('/video/(.+?)/', pmp_url)[0]
                    #log_utils.log('official pmp_url: {0} | pmp_id: {1}'.format(pmp_url, pmp_id))
                    streams.append(('paramount+', paramount_pattern + pmp_id))

            if streams:
                for s in streams:
                    sources.append({'source': s[0], 'quality': '1080p', 'language': 'en', 'url': s[1], 'direct': True, 'debridonly': False, 'external': True})

            return sources
        except:
            log_utils.log('Official scraper exc', 'source')
            return sources


    def resolve(self, url):
        return url


    def is_match(self, name, title, hdlr=None, aliases=None):
        try:
            name = name.lower()
            t = re.sub(r'(\+|\.|\(|\[|\s)(\d{4}|s\d+e\d+|s\d+|3d)(\.|\)|\]|\s|)(.+|)', '', name)
            t = cleantitle.get(t)
            titles = [cleantitle.get(title)]

            if aliases:
                if not isinstance(aliases, list):
                    from ast import literal_eval
                    aliases = literal_eval(aliases)
                try:
                    titles.extend([cleantitle.get(i['title']) for i in aliases])
                except:
                    pass

            if hdlr:
                return (t in titles and hdlr.lower() in name)
            return t in titles
        except:
            log_utils.log('is_match exc', 1)
            return True

    def netflix_ep_id(self, show_id, season, episode):
        header = {
            'Accept': 'application/json',
            'referer': 'https://unogs.com/',
            'referrer': 'http://unogs.com',
            'x-requested-with': 'XMLHttpRequest',
        }
        netflix_search_pattern = 'https://unogs.com/api/title/episodes?netflixid=%s'

        r = self.session.get(netflix_search_pattern % show_id, headers=header, timeout=5)
        r.raise_for_status()
        r.encoding = 'utf-8'
        apianswer = r.json()
        apifetch = [s['episodes'] for s in apianswer if s['season'] == int(season)][0]
        ep_id = str([e['epid'] for e in apifetch if e['epnum'] == int(episode)][0])

        return ep_id
