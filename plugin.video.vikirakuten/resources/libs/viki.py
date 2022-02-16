import time
import hmac
import hashlib
import base64
import json
import re
import datetime
import requests
import xml.etree.ElementTree as ET


class VikiAPI():

    _API_URL_TEMPLATE = 'https://api.viki.io'

    _DEVICE_ID = '112395910d' #'86085977d'  # used for android api
    _APP = '100005a'
    _APP0 ='100000a'
    _APP_VERSION = '6.11.3'
    _APP_SECRET = 'd96704b180208dbb2efa30fe44c48bd8690441af9f567ba8fd710a72badc85198f7472'

    _GEO_BYPASS = False
    _UA = 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Mobile Safari/537.36 Edg/97.0.1072.69'
    _token = None

    _ERRORS = {
        'geo': 'Sorry, this content is not available in your region.',
        'upcoming': 'Sorry, this content is not yet available.',
        'paywall': 'Sorry, this content is only available to Viki Pass Plus subscribers',
    }

    def _headers(self):
        return {
            'user-agent': self._UA,
            'x-client-user-agent': self._UA,
            'x-viki-app-ver': '4.0.96'
        }

    def _stream_headers(self, timestamp, sig):
        return {
            'X-Viki-manufacturer': 'vivo',
            'X-Viki-device-model': 'vivo 1606',
            'X-Viki-device-os-ver': '6.0.1',
            'X-Viki-connection-type': 'WIFI',
            'X-Viki-carrier': '',
            'X-Viki-as-id': '100005a-1625321982-3932',
            'timestamp': str(timestamp),
            'signature': str(sig),
            'x-viki-app-ver': self._APP_VERSION
        }

    def hash(self, query):

        timestamp = str(int(time.time()))
        sig = hmac.new(self._APP_SECRET.encode('ascii'), f'{query}&t={timestamp}'.encode('ascii'), hashlib.sha1).hexdigest()
        return timestamp, sig

    def decrypt(self, hashed):
        return ((base64.b64decode(hashed.encode('ascii'))).decode('ascii'))

    def get_HD_mpd(self, mpd_url):

        xml = requests.get(mpd_url).text
        root = ET.fromstring(xml)
        ns = {'': root.tag.partition('{')[2].rpartition('}')[0]}
        mpd_url = [i.text for i in root.findall(f'.//Representation/BaseURL', namespaces=ns) if i.text[-3:] == 'mpd'][0]
        if 'mpdhd_high' not in mpd_url:
            # Modify the URL to get 1080p
            mpd_url = mpd_url.replace('mpdhd', 'mpdhd_high')
        return mpd_url
    def api_query(self, path, version=4, full='', **kwargs):
        path += '?' if '?' not in path else '&'
        query = f'/v{version}/{path}app={self._APP}'
        if self._token:
            query += '&token=%s' % self._token
        if full:
            return f'{self._API_URL_TEMPLATE}{query}' + ''.join(f'&{name}={val}' for name, val in kwargs.items())
        return query + ''.join(f'&{name}={val}' for name, val in kwargs.items())

    def get_subs(self, movie_ID, lang):

        path = f'videos/{movie_ID}/subtitles/{lang}.srt'
        query = self.api_query(path)
        stamp, sig = self.hash(query)
        signedurl = f'{self._API_URL_TEMPLATE}{query}' + f'&t={stamp}&sig={sig}'
        return requests.get(signedurl).text

    def sign_query(self, path):
        #timestamp = int(time.time())
        query = self.api_query(path, version=5)
        timestamp, sig = self.hash(query)
        return timestamp, sig, f'{self._API_URL_TEMPLATE}{query}', f'{self._API_URL_TEMPLATE}{query}' + f'&t={timestamp}&sig={sig}'


    def call_api(
            self, path, video_id=None, data=None, query=None):
        if query is None:
            timestamp, sig, url, signedurl = self.sign_query(path)
        else:
            url = self.api_query(path, version=4, full=True)
        if data:
            data = json.dumps(data)
            headers = {'x-viki-app-ver': self._APP_VERSION}
            res = requests.post(url, headers=headers)
        else:
            res = requests.get(url, headers=self._stream_headers(timestamp, sig))
        return res

    def get_stream(self, movie_ID):

        manifest = []
        r_1 = self.call_api('playback_streams/{}.json?drms=dt3&device_id={}'.format(movie_ID, self._DEVICE_ID))
        if r_1.status_code == 200:
            manifest_SD = r_1.json()['main'][0]['url']
            manifest.append(self.get_HD_mpd(manifest_SD))
        r_2 = requests.get(f'https://www.viki.com/api/videos/{movie_ID}', headers=self._headers()).json()
        manifest_SD2 = self.decrypt(r_2['streams']['dash']['url'].split('?stream=')[1])

        manifest.append(self.get_HD_mpd(manifest_SD2))
        drm = json.loads(self.decrypt(r_2['drm']))
        return manifest, drm


    def _raise_error(self, error, fatal=True):
        if error is None:
            return
        msg = '%s said: %s' % ('self.IE_NAME', error)
        if fatal:
            print('fatal')
            #raise ExtractorError(msg, expected=True)
        else:
            self.report_warning(msg)

    def _check_errors(self, data):
        for reason, status in (data.get('blocking') or {}).items():
            if status and reason in self._ERRORS:
                #Błędy
                print(self._ERRORS[reason])
                #message = self._ERRORS[reason]
                if reason == 'geo':
                    print('raise_geo_restricted')
                    #self.raise_geo_restricted(msg=message)
                elif reason == 'paywall':
                    if try_get(data, lambda x: x['paywallable']['tvod']):
                        self._raise_error('This video is for rent only or TVOD (Transactional Video On demand)')
                    print('self.raise_login_required(message)')
                    #self.raise_login_required(message)
                print('self._raise_error(message)')
                #self._raise_error(message)

    def _real_initialize(self):
        self._login()

    def _login(self):
        username, password = self._get_login_info()
        if username is None:
            return

        self._token = self.call_api(
            'sessions.json', None, fatal=False,
            data={'username': username, 'password': password}).get('token')
        if not self._token:
            self.report_warning('Login Failed: Unable to get session token')




    def _real_extract(self, url):
        video_id = self._match_id(url)
        video = self.call_api(f'videos/{video_id}.json', video_id, query={})
        self._check_errors(video)

        title = try_get(video, lambda x: x['titles']['en'], str)
        episode_number = int_or_none(video.get('number'))
        if not title:
            title = 'Episode %d' % episode_number if video.get('type') == 'episode' else video.get('id') or video_id
            container_titles = try_get(video, lambda x: x['container']['titles'], dict) or {}
            container_title = self.dict_selection(container_titles, 'en')
            title = '%s - %s' % (container_title, title)

        thumbnails = [{
            'id': thumbnail_id,
            'url': thumbnail['url'],
        } for thumbnail_id, thumbnail in (video.get('images') or {}).items() if thumbnail.get('url')]

        resp = self.call_api(
            'playback_streams/%s.json?drms=dt1,dt2&device_id=%s' % (video_id, self._DEVICE_ID),
            video_id)['main'][0]

        stream_id = try_get(resp, lambda x: x['properties']['track']['stream_id'])
        subtitles = dict((lang, [{
            'ext': ext,
            'url': self._API_URL_TEMPLATE % self.api_query(
                f'videos/{video_id}/auth_subtitles/{lang}.{ext}', stream_id=stream_id)
        } for ext in ('srt', 'vtt')]) for lang in (video.get('subtitle_completions') or {}).keys())

        mpd_url = resp['url']
        # 1080p is hidden in another mpd which can be found in the current manifest content
        mpd_content = self._download_webpage(mpd_url, video_id, note='Downloading initial MPD manifest')

        mpd_url = self._search_regex(
            r'(?mi)<BaseURL>(http.+.mpd)', mpd_content, 'new manifest', default=mpd_url)
        formats = self._extract_mpd_formats(mpd_url, video_id)
        self._sort_formats(formats)

        return {
            'id': video_id,
            'formats': formats,
            'title': title,
            'description': self.dict_selection(video.get('descriptions', {}), 'en'),
            'duration': int_or_none(video.get('duration')),
            'timestamp': parse_iso8601(video.get('created_at')),
            'uploader': video.get('author'),
            'uploader_url': video.get('author_url'),
            'like_count': int_or_none(try_get(video, lambda x: x['likes']['count'])),
            'age_limit': parse_age_limit(video.get('rating')),
            'thumbnails': thumbnails,
            'subtitles': subtitles,
            'episode_number': episode_number,
        }


def try_get(src, getter, expected_type=None):
    if not isinstance(getter, (list, tuple)):
        getter = [getter]
    for get in getter:
        try:
            v = get(src)
        except (AttributeError, KeyError, TypeError, IndexError):
            pass
        else:
            if expected_type is None or isinstance(v, expected_type):
                return v

def int_or_none(v, scale=1, default=None, get_attr=None, invscale=1):
    if get_attr:
        if v is not None:
            v = getattr(v, get_attr, None)
    if v == '':
        v = None
    if v is None:
        return default
    try:
        return int(v) * invscale // scale
    except (ValueError, TypeError):
        return default


def extract_timezone(date_str):
    m = re.search(
        r'^.{8,}?(?P<tz>Z$| ?(?P<sign>\+|-)(?P<hours>[0-9]{2}):?(?P<minutes>[0-9]{2})$)',
        date_str)
    if not m:
        timezone = datetime.timedelta()
    else:
        date_str = date_str[:-len(m.group('tz'))]
        if not m.group('sign'):
            timezone = datetime.timedelta()
        else:
            sign = 1 if m.group('sign') == '+' else -1
            timezone = datetime.timedelta(
                hours=sign * int(m.group('hours')),
                minutes=sign * int(m.group('minutes')))
    return timezone, date_str


def parse_iso8601(date_str, delimiter='T', timezone=None):
    """ Return a UNIX timestamp from the given date """
    import calendar
    if date_str is None:
        return None

    date_str = re.sub(r'\.[0-9]+', '', date_str)

    if timezone is None:
        timezone, date_str = extract_timezone(date_str)

    try:
        date_format = '%Y-%m-%d{0}%H:%M:%S'.format(delimiter)
        dt = datetime.datetime.strptime(date_str, date_format) - timezone
        return calendar.timegm(dt.timetuple())
    except ValueError:
        pass

US_RATINGS = {
    'G': 0,
    'PG': 10,
    'PG-13': 13,
    'R': 16,
    'NC': 18,
}

TV_PARENTAL_GUIDELINES = {
    'TV-Y': 0,
    'TV-Y7': 7,
    'TV-G': 0,
    'TV-PG': 0,
    'TV-14': 14,
    'TV-MA': 17,
}

def parse_age_limit(s):
    if type(s) == int:
        return s if 0 <= s <= 21 else None
    if not isinstance(s, str):
        return None
    m = re.match(r'^(?P<age>\d{1,2})\+?$', s)
    if m:
        return int(m.group('age'))
    if s in US_RATINGS:
        return US_RATINGS[s]
    m = re.match(r'^TV[_-]?(%s)$' % '|'.join(k[3:] for k in TV_PARENTAL_GUIDELINES), s)
    if m:
        return TV_PARENTAL_GUIDELINES['TV-' + m.group(1)]
    return None

def dict_selection(dict_obj, preferred_key):
    if preferred_key in dict_obj:
        return dict_obj[preferred_key]
    return (list(filter(None, dict_obj.values())) or [None])[0]