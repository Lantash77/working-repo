# -*- coding: utf-8 -*-

"""
    Covenant Add-on

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

import json
import re


def json_load_as_str(file_handle):
    return byteify(json.load(file_handle, object_hook=byteify), ignore_dicts=True)


def json_loads_as_str(json_text):
    return byteify(json.loads(json_text, object_hook=byteify), ignore_dicts=True)


def byteify(data, ignore_dicts=False):
    if isinstance(data, str):
        return data
    if isinstance(data, list):
        return [byteify(item, ignore_dicts=True) for item in data]
    if isinstance(data, dict) and not ignore_dicts:
        return dict(
            [
                (byteify(key, ignore_dicts=True), byteify(value, ignore_dicts=True))
                for key, value in data.items()
            ]
        )
    return data


def title_key(title):
    try:
        if title is None:
            title = ""
        articles_en = ["the", "a", "an"]
        articles_de = ["der", "die", "das"]
        articles = articles_en + articles_de

        match = re.match("^((\w+)\s+)", title.lower())
        if match and match.group(2) in articles:
            offset = len(match.group(1))
        else:
            offset = 0

        return title[offset:]
    except:
        return title


def convert(data):
    if isinstance(data, bytes):
        return data.decode()
    if isinstance(data, (str, int)):
        return str(data)
    if isinstance(data, dict):
        return dict(map(convert, data.items()))
    if isinstance(data, tuple):
        return tuple(map(convert, data))
    if isinstance(data, list):
        return list(map(convert, data))
    if isinstance(data, set):
        return set(map(convert, data))
    else:
        return data
