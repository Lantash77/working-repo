# coding: utf-8
from __future__ import unicode_literals
import hashlib
import hmac
import json
import time

from .common import InfoExtractor
from ..utils import (
    ExtractorError,
    int_or_none,
    parse_age_limit,
    parse_iso8601,
    try_get,
)


class VikiBaseIE(InfoExtractor):

    _API_URL_TEMPLATE = 'https://api.viki.io%s'

    _DEVICE_ID = '86085977d'  # used for android api
    _APP = '100005a'
    _APP_VERSION = '6.11.3'
    _APP_SECRET = 'd96704b180208dbb2efa30fe44c48bd8690441af9f567ba8fd710a72badc85198f7472'

    _GEO_BYPASS = False
    _NETRC_MACHINE = 'viki'

    _token = None

    _ERRORS = {
        'geo': 'Sorry, this content is not available in your region.',
        'upcoming': 'Sorry, this content is not yet available.',
        'paywall': 'Sorry, this content is only available to Viki Pass Plus subscribers',
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

    def _api_query(self, path, version=4, **kwargs):
        path += '?' if '?' not in path else '&'
        query = f'/v{version}/{path}app={self._APP}'
        if self._token:
            query += '&token=%s' % self._token
        return query + ''.join(f'&{name}={val}' for name, val in kwargs.items())

    def _sign_query(self, path):
        timestamp = int(time.time())
        query = self._api_query(path, version=5)
        sig = hmac.new(
            self._APP_SECRET.encode('ascii'), f'{query}&t={timestamp}'.encode('ascii'), hashlib.sha1).hexdigest()
        return timestamp, sig, self._API_URL_TEMPLATE % query

    def _call_api(
            self, path, video_id, data=None, query=None, fatal=True):
        if query is None:
            timestamp, sig, url = self._sign_query(path)
        else:
            url = self._API_URL_TEMPLATE % self._api_query(path, version=4)
        resp = self._download_json(
            url, video_id, fatal=fatal, query=query,
            data=json.dumps(data).encode('utf-8') if data else None,
            headers=({'x-viki-app-ver': self._APP_VERSION} if data
                     else self._stream_headers(timestamp, sig) if query is None
                     else None), expected_status=400) or {}

        self._raise_error(resp.get('error'), fatal)
        return resp

    def _raise_error(self, error, fatal=True):
        if error is None:
            return
        msg = '%s said: %s' % (self.IE_NAME, error)
        if fatal:
            raise ExtractorError(msg, expected=True)
        else:
            self.report_warning(msg)

    def _check_errors(self, data):
        for reason, status in (data.get('blocking') or {}).items():
            if status and reason in self._ERRORS:
                message = self._ERRORS[reason]
                if reason == 'geo':
                    self.raise_geo_restricted(msg=message)
                elif reason == 'paywall':
                    if try_get(data, lambda x: x['paywallable']['tvod']):
                        self._raise_error('This video is for rent only or TVOD (Transactional Video On demand)')
                    self.raise_login_required(message)
                self._raise_error(message)

    def _real_initialize(self):
        self._login()

    def _login(self):
        username, password = self._get_login_info()
        if username is None:
            return

        self._token = self._call_api(
            'sessions.json', None, fatal=False,
            data={'username': username, 'password': password}).get('token')
        if not self._token:
            self.report_warning('Login Failed: Unable to get session token')

    @staticmethod
    def dict_selection(dict_obj, preferred_key):
        if preferred_key in dict_obj:
            return dict_obj[preferred_key]
        return (list(filter(None, dict_obj.values())) or [None])[0]


class VikiIE(VikiBaseIE):
    IE_NAME = 'viki'


    def _real_extract(self, url):
        video_id = self._match_id(url)
        video = self._call_api(f'videos/{video_id}.json', video_id, query={})
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

        resp = self._call_api(
            'playback_streams/%s.json?drms=dt1,dt2&device_id=%s' % (video_id, self._DEVICE_ID),
            video_id)['main'][0]

        stream_id = try_get(resp, lambda x: x['properties']['track']['stream_id'])
        subtitles = dict((lang, [{
            'ext': ext,
            'url': self._API_URL_TEMPLATE % self._api_query(
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


class VikiChannelIE(VikiBaseIE):
    IE_NAME = 'viki:channel'


    _video_types = ('episodes', 'movies', 'clips', 'trailers')

    def _entries(self, channel_id):
        params = {
            'app': self._APP, 'token': self._token, 'only_ids': 'true',
            'direction': 'asc', 'sort': 'number', 'per_page': 30
        }
        video_types = self._configuration_arg('video_types') or self._video_types
        for video_type in video_types:
            if video_type not in self._video_types:
                self.report_warning(f'Unknown video_type: {video_type}')
            page_num = 0
            while True:
                page_num += 1
                params['page'] = page_num
                res = self._call_api(
                    f'containers/{channel_id}/{video_type}.json', channel_id, query=params, fatal=False)

                for video_id in res.get('response') or []:
                    yield self.url_result(f'https://www.viki.com/videos/{video_id}', VikiIE.ie_key(), video_id)
                if not res.get('more'):
                    break

    def _real_extract(self, url):
        channel_id = self._match_id(url)
        channel = self._call_api('containers/%s.json' % channel_id, channel_id)
        self._check_errors(channel)
        return self.playlist_result(
            self._entries(channel_id), channel_id,
            self.dict_selection(channel['titles'], 'en'),
            self.dict_selection(channel['descriptions'], 'en'))
