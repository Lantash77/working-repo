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

