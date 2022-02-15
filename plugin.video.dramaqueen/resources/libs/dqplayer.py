import requests
import re

sess = requests.session()

UA = 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Mobile Safari/537.36 Edg/97.0.1072.69'

def fetch(url):
    id = url.split("/")[-1]
    base_url = re.findall('(.+?://.+?/)', url)[0]

    # main
    headers = {
        'user-agent': UA,
        'referer': 'https://www.dramaqueen.pl/',
    }

    r = sess.get(url, headers=headers)

    # activate
    activate_url = re.findall(';loadUrl\(\"(.+?)\",', r.text)[0].split(";")[-1].replace('loadUrl("', '')
    headers_activate = {
        'user-agent': UA,
        'referer': base_url
    }

    r_activate = sess.get(activate_url, headers=headers_activate)
    # src
    src_url = re.findall('e.loadSource\(\"(.+?)\"\);', r.text)[0]
    headers_src = {
        'user-agent': UA,
        'referer': url,
    }

    r_src = sess.get(src_url, headers=headers_src)
    res_list = re.findall('.*/video.drm?.*', r_src.text)
    res = res_list[-1]

    # hls
    strmUrl = base_url + id + '/' + res

    return strmUrl, headers_src, activate_url, headers_activate


