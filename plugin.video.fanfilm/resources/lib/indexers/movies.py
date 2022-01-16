# -*- coding: utf-8 -*-

"""
    Fanfilm Add-on

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

import datetime
import json
import os
import re
import sys
import urllib
import requests

try:
    import urllib.parse as urllib
except:
    pass
from resources.lib.indexers import navigator
from ptw.libraries import cache
from ptw.libraries import cleangenre
from ptw.libraries import cleantitle
from ptw.libraries import client
from ptw.libraries import control
from ptw.libraries import metacache
from ptw.libraries import playcount
from ptw.libraries import trakt
from ptw.libraries import utils
from ptw.libraries import views
from ptw.libraries import apis
from ptw.libraries.utils import convert

params = (
    dict(urllib.parse_qsl(sys.argv[2].replace("?", "")))
    if len(sys.argv) > 1
    else dict()
)

action = params.get("action")

#moviessort = control.setting("movies.sort")
listscount = control.setting("lists.count")

#if moviessort == "0":
#    moviessort = "moviemeter,asc"
#elif moviessort == "1":
#    moviessort = "year,desc"
moviessort = "moviemeter,asc"

class movies:
    def __init__(self):
        self.list = []

        self.session = requests.Session()

        self.imdb_link = "http://www.imdb.com"
        self.trakt_link = "https://api.trakt.tv"
        self.datetime = datetime.datetime.utcnow() - datetime.timedelta(hours=5)
        self.systime = (self.datetime).strftime("%Y%m%d%H%M%S%f")
        self.year_date = (self.datetime - datetime.timedelta(days=365)).strftime(
            "%Y-%m-%d"
        )
        self.today_date = (self.datetime).strftime("%Y-%m-%d")
        self.trakt_user = control.setting("trakt.user").strip()
        self.imdb_user = control.setting("imdb.user").replace("ur", "")
        self.lang = control.apiLanguage()["tmdb"]
        self.tm_user = apis.tmdb_API#control.setting("tm.user")
        self.tmdb_api_link = 'https://api.themoviedb.org/3/movie/%s?api_key=%s&language=%s&append_to_response=credits,external_ids' % ('%s', self.tm_user, self.lang)
        self.tmdb_by_imdb = 'https://api.themoviedb.org/3/find/%s?api_key=%s&external_source=imdb_id' % ('%s', self.tm_user)
        self.tmdb_arts = 'https://api.themoviedb.org/3/movie/%s/images?api_key=%s&include_image_language=pl,en' % (
        '%s', self.tm_user)
        self.tmdb_providers = 'https://api.themoviedb.org/3/movie/%s/watch/providers?api_key=%s' % ('%s', self.tm_user)
        self.fanart_tv_user = apis.fanarttv_client_key#control.setting("fanart.tv.user")
        self.fanart_tv_headers = {"api-key": apis.fanarttv_API_key}#control.setting("fanart.tv.dev")}
        if not self.fanart_tv_user == "":
            self.fanart_tv_headers.update({"client-key": self.fanart_tv_user})
        self.user = str(control.setting("fanart.tv.user")) + str(
            control.setting("tm.user")
        )
        self.hidecinema = control.setting("hidecinema")
        self.hidecinema_rollback = int(control.setting("hidecinema.rollback"))
        self.hidecinema_rollback2 = self.hidecinema_rollback * 30
        self.hidecinema_date = (
            datetime.date.today() - datetime.timedelta(days=self.hidecinema_rollback2)
        ).strftime("%Y-%m")

        self.search_link = "https://api.trakt.tv/search/movie?limit=20&page=1&query="
        self.fanart_tv_art_link = "http://webservice.fanart.tv/v3/movies/%s"
        self.fanart_tv_level_link = "https://webservice.fanart.tv/v3/level"
        self.tm_art_link = (
            "https://api.themoviedb.org/3/movie/%s/images?api_key=%s&language=en-US&include_image_language=en,%s,null"
            % ("%s", self.tm_user, self.lang)
        )
        self.tm_img_link = "https://image.tmdb.org/t/p/w%s%s"

        self.persons_link = "https://www.imdb.com/search/name?count=100&name="
        self.personlist_link = (
            "https://www.imdb.com/search/name?count=100&gender=male,female"
        )
        self.person_link = (
            "https://www.imdb.com/search/title?title_type=feature,tv_movie&production_status=released&role=%s&sort="
            + moviessort
            + "&count="
            + listscount
            + "&start=1"
        )
        self.keyword_link = (
            "https://www.imdb.com/search/title?title_type=feature,tv_movie,documentary&num_votes=100,&release_date=,date[0]&keywords=%s&sort="
            + moviessort
            + "&count="
            + listscount
            + "&start=1"
        )
        self.theaters_link = (
            "https://www.imdb.com/search/title?title_type=feature&num_votes=1000,&release_date=date[120],date[0]&sort="
            + moviessort
            + "&count="
            + listscount
            + "&start=1"
        )
        self.year_link = (
            "https://www.imdb.com/search/title?title_type=feature,tv_movie&num_votes=100,&production_status=released&year=%s,%s&sort="
            + moviessort
            + "&count="
            + listscount
            + "&start=1"
        )
        #       self.year_link = 'https://www.imdb.com/search/title?title_type=feature,tv_movie&num_votes=100,&production_status=released&year=%s,%s&sort=' + moviessort + '&count=' + listscount + '&start=1'
        self.action_link = (
            "https://www.imdb.com/search/title?title_type=feature,tv_movie,documentary&num_votes=100,&release_date=,date[0]&genres=action&sort="
            + moviessort
            + "&count="
            + listscount
            + "&start=1"
        )
        self.adventure_link = (
            "https://www.imdb.com/search/title?title_type=feature,tv_movie,documentary&num_votes=100,&release_date=,date[0]&genres=adventure&sort="
            + moviessort
            + "&count="
            + listscount
            + "&start=1"
        )
        self.animation_link = (
            "https://www.imdb.com/search/title?title_type=feature,tv_movie,documentary&num_votes=100,&release_date=,date[0]&genres=animation&sort="
            + moviessort
            + "&count="
            + listscount
            + "&start=1"
        )
        self.anime_link = (
            "https://www.imdb.com/search/title?title_type=feature,tv_movie,documentary&num_votes=100,&release_date=,date[0]&keywords=anime&sort="
            + moviessort
            + "&count="
            + listscount
            + "&start=1"
        )
        self.biography_link = (
            "https://www.imdb.com/search/title?title_type=feature,tv_movie,documentary&num_votes=100,&release_date=,date[0]&genres=biography&sort="
            + moviessort
            + "&count="
            + listscount
            + "&start=1"
        )
        self.comedy_link = (
            "https://www.imdb.com/search/title?title_type=feature,tv_movie,documentary&num_votes=100,&release_date=,date[0]&genres=comedy&sort="
            + moviessort
            + "&count="
            + listscount
            + "&start=1"
        )
        self.crime_link = (
            "https://www.imdb.com/search/title?title_type=feature,tv_movie,documentary&num_votes=100,&release_date=,date[0]&genres=crime&sort="
            + moviessort
            + "&count="
            + listscount
            + "&start=1"
        )
        self.documentary_link = (
            "https://www.imdb.com/search/title?title_type=feature,tv_movie,documentary&num_votes=100,&release_date=,date[0]&genres=documentary&sort="
            + moviessort
            + "&count="
            + listscount
            + "&start=1"
        )
        self.drama_link = (
            "https://www.imdb.com/search/title?title_type=feature,tv_movie,documentary&num_votes=100,&release_date=,date[0]&genres=drama&sort="
            + moviessort
            + "&count="
            + listscount
            + "&start=1"
        )
        self.family_link = (
            "https://www.imdb.com/search/title?title_type=feature,tv_movie,documentary&num_votes=100,&release_date=,date[0]&genres=family&sort="
            + moviessort
            + "&count="
            + listscount
            + "&start=1"
        )
        self.fantasy_link = (
            "https://www.imdb.com/search/title?title_type=feature,tv_movie,documentary&num_votes=100,&release_date=,date[0]&genres=fantasy&sort="
            + moviessort
            + "&count="
            + listscount
            + "&start=1"
        )
        self.history_link = (
            "https://www.imdb.com/search/title?title_type=feature,tv_movie,documentary&num_votes=100,&release_date=,date[0]&genres=history&sort="
            + moviessort
            + "&count="
            + listscount
            + "&start=1"
        )
        self.horror_link = (
            "https://www.imdb.com/search/title?title_type=feature,tv_movie,documentary&num_votes=100,&release_date=,date[0]&genres=horror&sort="
            + moviessort
            + "&count="
            + listscount
            + "&start=1"
        )
        self.music_link = (
            "https://www.imdb.com/search/title?title_type=feature,tv_movie,documentary&num_votes=100,&release_date=,date[0]&genres=music&sort="
            + moviessort
            + "&count="
            + listscount
            + "&start=1"
        )
        self.musical_link = (
            "https://www.imdb.com/search/title?title_type=feature,tv_movie,documentary&num_votes=100,&release_date=,date[0]&genres=musical&sort="
            + moviessort
            + "&count="
            + listscount
            + "&start=1"
        )
        self.mystery_link = (
            "https://www.imdb.com/search/title?title_type=feature,tv_movie,documentary&num_votes=100,&release_date=,date[0]&genres=mystery&sort="
            + moviessort
            + "&count="
            + listscount
            + "&start=1"
        )
        self.romance_link = (
            "https://www.imdb.com/search/title?title_type=feature,tv_movie,documentary&num_votes=100,&release_date=,date[0]&genres=romance&sort="
            + moviessort
            + "&count="
            + listscount
            + "&start=1"
        )
        self.sci_fi_link = (
            "https://www.imdb.com/search/title?title_type=feature,tv_movie,documentary&num_votes=100,&release_date=,date[0]&genres=sci_fi&sort="
            + moviessort
            + "&count="
            + listscount
            + "&start=1"
        )
        self.sport_link = (
            "https://www.imdb.com/search/title?title_type=feature,tv_movie,documentary&num_votes=100,&release_date=,date[0]&genres=sport&sort="
            + moviessort
            + "&count="
            + listscount
            + "&start=1"
        )
        self.thriller_link = (
            "https://www.imdb.com/search/title?title_type=feature,tv_movie,documentary&num_votes=100,&release_date=,date[0]&genres=thriller&sort="
            + moviessort
            + "&count="
            + listscount
            + "&start=1"
        )
        self.war_link = (
            "https://www.imdb.com/search/title?title_type=feature,tv_movie,documentary&num_votes=100,&release_date=,date[0]&genres=war&sort="
            + moviessort
            + "&count="
            + listscount
            + "&start=1"
        )
        self.western_link = (
            "https://www.imdb.com/search/title?title_type=feature,tv_movie,documentary&num_votes=100,&release_date=,date[0]&genres=western&sort="
            + moviessort
            + "&count="
            + listscount
            + "&start=1"
        )

        if self.hidecinema == "true":
            self.popular_link = (
                "https://www.imdb.com/search/title?title_type=feature,tv_movie&num_votes=1000,&production_status=released&groups=top_1000&release_date=,"
                + self.hidecinema_date
                + "&sort=moviemeter,asc&count="
                + listscount
                + "&start=1"
            )
            self.views_link = (
                "https://www.imdb.com/search/title?title_type=feature,tv_movie&num_votes=1000,&production_status=released&sort=num_votes,desc&release_date=,"
                + self.hidecinema_date
                + "&count="
                + listscount
                + "&start=1"
            )
            self.featured_link = (
                "https://www.imdb.com/search/title?title_type=feature,tv_movie&num_votes=1000,&production_status=released&release_date=date[365],date[90]&sort="
                + moviessort
                + "&count="
                + listscount
                + "&start=1"
            )
            self.genre_link = (
                "https://www.imdb.com/search/title?title_type=feature,tv_movie,documentary&num_votes=100,&release_date=,"
                + self.hidecinema_date
                + "&genres=%s&sort="
                + moviessort
                + "&count="
                + listscount
                + "&start=1"
            )
            self.language_link = (
                "https://www.imdb.com/search/title?title_type=feature,tv_movie&num_votes=100,&production_status=released&primary_language=%s&sort="
                + moviessort
                + "&release_date=,"
                + self.hidecinema_date
                + "&count="
                + listscount
                + "&start=1"
            )
            self.certification_link = (
                "https://www.imdb.com/search/title?title_type=feature,tv_movie&num_votes=100,&production_status=released&certificates=us:%s&sort="
                + moviessort
                + "&release_date=,"
                + self.hidecinema_date
                + "&count="
                + listscount
                + "&start=1"
            )
            self.boxoffice_link = (
                "https://www.imdb.com/search/title?title_type=feature,tv_movie&production_status=released&sort=boxoffice_gross_us,desc&release_date=,"
                + self.hidecinema_date
                + "&count="
                + listscount
                + "&start=1"
            )
            self.thcenturyfox_link = (
                "https://www.imdb.com/search/title?companies=fox&production_status=released&title_type=feature,tv_movie&release_date=,"
                + self.hidecinema_date
                + "&sort="
                + moviessort
                + "&count="
                + listscount
                + "&start=1"
            )
            self.dreamworks_link = (
                "https://www.imdb.com/search/title?companies=dreamworks&production_status=released&title_type=feature,tv_movie&release_date=,"
                + self.hidecinema_date
                + "&sort="
                + moviessort
                + "&count="
                + listscount
                + "&start=1"
            )
            self.mgm_link = (
                "https://www.imdb.com/search/title?companies=mgm&production_status=released&title_type=feature,tv_movie&release_date=,"
                + self.hidecinema_date
                + "&sort="
                + moviessort
                + "&count="
                + listscount
                + "&start=1"
            )
            self.paramount_link = (
                "https://www.imdb.com/search/title?companies=paramount&production_status=released&title_type=feature,tv_movie&release_date=,"
                + self.hidecinema_date
                + "&sort="
                + moviessort
                + "&count="
                + listscount
                + "&start=1"
            )
            self.sony_link = (
                "https://www.imdb.com/search/title?companies=sony&production_status=released&title_type=feature,tv_movie&release_date=,"
                + self.hidecinema_date
                + "&sort="
                + moviessort
                + "&count="
                + listscount
                + "&start=1"
            )
            self.universal_link = (
                "https://www.imdb.com/search/title?companies=universal&production_status=released&title_type=feature,tv_movie&release_date=,"
                + self.hidecinema_date
                + "&sort="
                + moviessort
                + "&count="
                + listscount
                + "&start=1"
            )
            self.waltdisney_link = (
                "https://www.imdb.com/search/title?companies=disney&production_status=released&title_type=feature,tv_movie&release_date=,"
                + self.hidecinema_date
                + "&sort="
                + moviessort
                + "&count="
                + listscount
                + "&start=1"
            )
            self.warnerbross_link = (
                "https://www.imdb.com/search/title?companies=warner&production_status=released&title_type=feature,tv_movie&release_date=,"
                + self.hidecinema_date
                + "&sort="
                + moviessort
                + "&count="
                + listscount
                + "&start=1"
            )
            # https://www.imdb.com/list/ls093971121/?st_dt=&mode=detail&page=1&title_type=tvMovie&ref_=ttls_ref_typ
            self.netflix_link = (
                "https://www.imdb.com/list/ls093971121/?production_status=released&title_type=tvMovie&release_date=,"
                + self.hidecinema_date
                + "&sort="
                + moviessort
                + "&count="
                + listscount
                + "&start=1&ref_=ttls_ref_typ&st_dt=&mode=detail"
            )
        else:
            self.popular_link = (
                "https://www.imdb.com/search/title?title_type=feature,tv_movie&num_votes=1000,&production_status=released&groups=top_1000&sort=moviemeter,asc&count="
                + listscount
                + "&start=1"
            )
            self.views_link = (
                "https://www.imdb.com/search/title?title_type=feature,tv_movie&num_votes=1000,&production_status=released&sort=num_votes,desc&count="
                + listscount
                + "&start=1"
            )
            self.featured_link = (
                "https://www.imdb.com/search/title?title_type=feature,tv_movie&num_votes=1000,&production_status=released&release_date=date[365],date[60]&sort="
                + moviessort
                + "&count="
                + listscount
                + "&start=1"
            )
            self.genre_link = (
                "https://www.imdb.com/search/title?title_type=feature,tv_movie,documentary&num_votes=100,&release_date=,date[0]&genres=%s&sort="
                + moviessort
                + "&count="
                + listscount
                + "&start=1"
            )
            self.language_link = (
                "https://www.imdb.com/search/title?title_type=feature,tv_movie&num_votes=100,&production_status=released&primary_language=%s&sort="
                + moviessort
                + "&count="
                + listscount
                + "&start=1"
            )
            self.certification_link = (
                "https://www.imdb.com/search/title?title_type=feature,tv_movie&num_votes=100,&production_status=released&certificates=us:%s&sort="
                + moviessort
                + "&count="
                + listscount
                + "&start=1"
            )
            self.boxoffice_link = (
                "https://www.imdb.com/search/title?title_type=feature,tv_movie&production_status=released&sort=boxoffice_gross_us,desc&count="
                + listscount
                + "&start=1"
            )
            self.thcenturyfox_link = (
                "https://www.imdb.com/search/title?companies=fox&production_status=released&title_type=feature,tv_movie&sort="
                + moviessort
                + "&count="
                + listscount
                + "&start=1"
            )
            self.dreamworks_link = (
                "https://www.imdb.com/search/title?companies=dreamworks&production_status=released&title_type=feature,tv_movie&sort="
                + moviessort
                + "&count="
                + listscount
                + "&start=1"
            )
            self.mgm_link = (
                "https://www.imdb.com/search/title?companies=mgm&production_status=released&title_type=feature,tv_movie&sort="
                + moviessort
                + "&count="
                + listscount
                + "&start=1"
            )
            self.paramount_link = (
                "https://www.imdb.com/search/title?companies=paramount&production_status=released&title_type=feature,tv_movie&sort="
                + moviessort
                + "&count="
                + listscount
                + "&start=1"
            )
            self.sony_link = (
                "https://www.imdb.com/search/title?companies=sony&production_status=released&title_type=feature,tv_movie&sort="
                + moviessort
                + "&count="
                + listscount
                + "&start=1"
            )
            self.universal_link = (
                "https://www.imdb.com/search/title?companies=universal&production_status=released&title_type=feature,tv_movie&sort="
                + moviessort
                + "&count="
                + listscount
                + "&start=1"
            )
            self.waltdisney_link = (
                "https://www.imdb.com/search/title?companies=disney&production_status=released&title_type=feature,tv_movie&sort="
                + moviessort
                + "&count="
                + listscount
                + "&start=1"
            )
            self.warnerbross_link = (
                "https://www.imdb.com/search/title?companies=warner&production_status=released&title_type=feature,tv_movie&sort="
                + moviessort
                + "&count="
                + listscount
                + "&start=1"
            )
            self.netflix_link = (
                "https://www.imdb.com/list/ls093971121/?production_status=released&title_type=tvMovie&sort="
                + moviessort
                + "&count="
                + listscount
                + "&start=1&ref_=ttls_ref_typ&st_dt=&mode=detail"
            )

        self.added_link = (
            "https://www.imdb.com/search/title?title_type=feature,tv_movie&languages=en&num_votes=500,&production_status=released&release_date=%s,%s&sort=release_date,desc&count=20&start=1"
            % (self.year_date, self.today_date)
        )
        self.trending_link = "http://api.trakt.tv/movies/trending?limit=40&page=1"
        self.traktlists_link = "http://api.trakt.tv/users/me/lists"
        self.traktlikedlists_link = (
            "http://api.trakt.tv/users/likes/lists?limit=1000000"
        )
        self.traktlist_link = "http://api.trakt.tv/users/%s/lists/%s/items"
        self.traktcollection_link = "http://api.trakt.tv/users/me/collection/movies"
        self.traktwatchlist_link = "http://api.trakt.tv/users/me/watchlist/movies"
        self.traktfeatured_link = "http://api.trakt.tv/recommendations/movies?limit=40"
        self.trakthistory_link = (
            "http://api.trakt.tv/users/me/history/movies?limit=40&page=1"
        )
        self.imdblists_link = (
            "https://www.imdb.com/user/ur%s/lists?tab=all&sort=mdfd&order=desc&filter=titles"
            % self.imdb_user
        )
        self.imdblist_link = "https://www.imdb.com/list/%s/?view=detail&sort=alpha,asc&title_type=movie,short,tvMovie,tvSpecial,video&start=1"
        self.imdblist2_link = "https://www.imdb.com/list/%s/?view=detail&sort=date_added,desc&title_type=movie,short,tvMovie,tvSpecial,video&start=1"
        self.imdbwatchlist_link = (
            "https://www.imdb.com/user/ur%s/watchlist?sort=alpha,asc" % self.imdb_user
        )
        self.imdbwatchlist2_link = (
            "https://www.imdb.com/user/ur%s/watchlist?sort=date_added,desc"
            % self.imdb_user
        )
        self.imdbUserLists_link = (
            "https://www.imdb.com/list/%s/?view=detail&sort=alpha,asc&title_type=movie,tvMovie&count="
            + listscount
            + "&start=1"
        )

        self.y50_link = (
            "https://www.imdb.com/search/title?title_type=feature&release_date=1950-01-01,1959-12-31&sort=moviemeter,asc&count="
            + listscount
            + "&start=1"
        )
        self.y60_link = (
            "https://www.imdb.com/search/title?title_type=feature&release_date=1960-01-01,1969-12-31&sort=moviemeter,asc&count="
            + listscount
            + "&start=1"
        )
        self.y70_link = (
            "https://www.imdb.com/search/title?title_type=feature&release_date=1970-01-01,1979-12-31&sort=moviemeter,asc&count="
            + listscount
            + "&start=1"
        )
        self.y80_link = (
            "https://www.imdb.com/search/title?title_type=feature&release_date=1980-01-01,1989-12-31&sort=moviemeter,asc&count="
            + listscount
            + "&start=1"
        )
        self.y90_link = (
            "https://www.imdb.com/search/title?title_type=feature&release_date=1990-01-01,1999-12-31&sort=moviemeter,asc&count="
            + listscount
            + "&start=1"
        )
        self.y2000_link = (
            "https://www.imdb.com/search/title?title_type=feature&release_date=2000-01-01,2009-12-31&sort=moviemeter,asc&count="
            + listscount
            + "&start=1"
        )
        self.y2010_link = (
            "https://www.imdb.com/search/title?title_type=feature&release_date=2010-01-01,2019-12-31&sort=moviemeter,asc&count="
            + listscount
            + "&start=1"
        )
        self.y2020_link = (
            "https://www.imdb.com/search/title?title_type=feature&release_date=2020-01-01,date[90]&sort=moviemeter,asc&count="
            + listscount
            + "&start=1"
        )
        self.oscars_link = (
            "https://www.imdb.com/search/title?groups=oscar_winner&sort=year,desc&count="
            + listscount
            + "&start=1"
        )
        self.oscarsnom_link = (
            "https://www.imdb.com/search/title?groups=oscar_nominee&sort=year,desc&count="
            + listscount
            + "&start=1"
        )
        self.oscarsbestmovie_link = (
            "https://www.imdb.com/search/title?groups=best_picture_winner&sort=year,desc&count="
            + listscount
            + "&start=1"
        )
        self.oscarsbestmovienom_link = (
            "https://www.imdb.com/search/title?groups=oscar_best_picture_nominees&sort=year,desc&count="
            + listscount
            + "&start=1"
        )
        self.oscarsbestdir_link = (
            "https://www.imdb.com/search/title?groups=best_director_winner&sort=year,desc&count="
            + listscount
            + "&start=1"
        )
        self.oscarsbestdirnom_link = (
            "https://www.imdb.com/search/title?groups=oscar_best_director_nominees&sort=year,desc&count="
            + listscount
            + "&start=1"
        )
        self.razzie_link = (
            "https://www.imdb.com/search/title?groups=razzie_winner&sort=year,desc&count="
            + listscount
            + "&start=1"
        )
        self.razzienom_link = (
            "https://www.imdb.com/search/title?groups=razzie_nominee&sort=year,desc&count="
            + listscount
            + "&start=1"
        )

    def get(self, url, idx=True, create_directory=True):
        try:
            try:
                url = getattr(self, url + "_link")
            except:
                pass

            try:
                u = urllib.urlparse(url).netloc.lower()
            except:
                pass

            if u in self.trakt_link and "/users/" in url:
                try:
                    if url == self.trakthistory_link:
                        raise Exception()
                    if not "/users/me/" in url:
                        raise Exception()
                    if trakt.getActivity() > cache.timeout(
                        self.trakt_list, url, self.trakt_user
                    ):
                        raise Exception()
                    self.list = cache.get(self.trakt_list, 720, url, self.trakt_user)
                except:
                    self.list = cache.get(self.trakt_list, 0, url, self.trakt_user)

                if "/users/me/" in url and "/collection/" in url:
                    self.list = sorted(
                        self.list, key=lambda k: utils.title_key(k["title"])
                    )

                if idx == True:
                    self.worker()

            elif u in self.trakt_link and self.search_link in url:
                self.list = cache.get(self.trakt_list, 1, url, self.trakt_user)
                if idx == True:
                    self.worker(level=0)

            elif u in self.trakt_link:
                self.list = cache.get(self.trakt_list, 24, url, self.trakt_user)
                if idx == True:
                    self.worker()

            elif u in self.imdb_link and ("/user/" in url or "/list/" in url):
                self.list = cache.get(self.imdb_list, 0, url)
                if idx == True:
                    self.worker()

            elif u in self.imdb_link:
                self.list = cache.get(self.imdb_list, 24, url)
                if idx == True:
                    self.worker()

            if idx == True and create_directory == True:
                self.movieDirectory(self.list)
            return self.list
        except Exception as e:
            print(e)
            return

    def widget(self):
        setting = control.setting("movie.widget")

        if setting == "2":
            self.get(self.trending_link)
        elif setting == "3":
            self.get(self.popular_link)
        elif setting == "4":
            self.get(self.theaters_link)
        elif setting == "5":
            self.get(self.added_link)
        else:
            self.get(self.featured_link)

    def search(self):

        navigator.navigator().addDirectoryItem(
            32603, "movieSearchnew", "search.png", "DefaultMovies.png"
        )

        from sqlite3 import dbapi2 as database

        dbcon = database.connect(control.searchFile)
        dbcur = dbcon.cursor()

        try:
            dbcur.executescript(
                "CREATE TABLE IF NOT EXISTS movies (ID Integer PRIMARY KEY AUTOINCREMENT, term);"
            )
        except:
            pass

        dbcur.execute("SELECT * FROM movies ORDER BY ID DESC")
        lst = []

        delete_option = False
        for (id, term) in dbcur.fetchall():
            if term not in str(lst):
                delete_option = True
                navigator.navigator().addDirectoryItem(
                    term,
                    "movieSearchterm&name=%s" % term,
                    "search.png",
                    "DefaultMovies.png",
                )
                lst += [(term)]
        dbcur.close()

        if delete_option:
            navigator.navigator().addDirectoryItem(
                32605, "clearCacheSearch", "tools.png", "DefaultAddonProgram.png"
            )

        navigator.navigator().endDirectory()

    def search_new(self):
        control.idle()
        t = control.lang(32010).encode("utf-8")
        k = control.keyboard("", t)
        k.doModal()
        q = k.getText() if k.isConfirmed() else None

        if q == None or q == "":
            return

        q = cleantitle.normalize(q)  # for polish characters
        control.busy()

        from sqlite3 import dbapi2 as database

        dbcon = database.connect(control.searchFile)
        dbcur = dbcon.cursor()
        dbcur.execute("INSERT INTO movies VALUES (?,?)", (None, q))
        dbcon.commit()
        dbcur.close()
        # url = self.search_link + urllib.quote_plus(q)
        # url = '%s?action=moviePage&url=%s' % (sys.argv[0], urllib.quote_plus(url))
        movies.get(self, self.search_link + q)
        control.idle()

    def search_term(self, name):
        control.busy()

        # url = self.search_link + urllib.quote_plus(name)
        # url = '%s?action=moviePage&url=%s' % (sys.argv[0], urllib.quote_plus(url))
        movies.get(self, self.search_link + urllib.quote_plus(name))
        control.idle()

    def person(self):
        try:
            control.idle()

            t = control.lang(32010).encode("utf-8")
            k = control.keyboard("", t)
            k.doModal()
            q = k.getText() if k.isConfirmed() else None

            if q == None or q == "":
                return

            q = cleantitle.normalize(q)  # for polish characters
            control.busy()
            # url = self.persons_link + urllib.quote_plus(q)
            # url = '%s?action=moviePersons&url=%s' % (sys.argv[0], urllib.quote_plus(url))
            movies.persons(self, self.persons_link + q)
            control.idle()
        except Exception as e:
            print(e)
            return

#    def genres(self):
#        genres = [
#            ("Action", "action", True),
#            ("Adventure", "adventure", True),
#            ("Animation", "animation", True),
#            ("Anime", "anime", False),
#            ("Biography", "biography", True),
#            ("Comedy", "comedy", True),
#            ("Crime", "crime", True),
#            ("Documentary", "documentary", True),
#            ("Drama", "drama", True),
#            ("Family", "family", True),
#            ("Fantasy", "fantasy", True),
#            ("History", "history", True),
#            ("Horror", "horror", True),
#            ("Music ", "music", True),
#            ("Musical", "musical", True),
#            ("Mystery", "mystery", True),
#            ("Romance", "romance", True),
#            ("Science Fiction", "sci_fi", True),
#            ("Sport", "sport", True),
#            ("Thriller", "thriller", True),
#            ("War", "war", True),
#            ("Western", "western", True),
#        ]
#
#        for i in genres:
#            self.list.append(
#                {
#                    "name": cleangenre.lang(i[0], self.lang),
#                    "url": self.genre_link % i[1] if i[2] else self.keyword_link % i[1],
#                    "image": "movieGenres.jpg",
#                    "action": "movies",
#                }
#            )
#
#        self.addDirectory(self.list)
#        return self.list

    def languages(self):
        languages = [
            ("Arabic", "ar"),
            ("Bosnian", "bs"),
            ("Bulgarian", "bg"),
            ("Chinese", "zh"),
            ("Croatian", "hr"),
            ("Dutch", "nl"),
            ("English", "en"),
            ("Finnish", "fi"),
            ("French", "fr"),
            ("German", "de"),
            ("Greek", "el"),
            ("Hebrew", "he"),
            ("Hindi ", "hi"),
            ("Hungarian", "hu"),
            ("Icelandic", "is"),
            ("Italian", "it"),
            ("Japanese", "ja"),
            ("Korean", "ko"),
            ("Macedonian", "mk"),
            ("Norwegian", "no"),
            ("Persian", "fa"),
            ("Polish", "pl"),
            ("Portuguese", "pt"),
            ("Punjabi", "pa"),
            ("Romanian", "ro"),
            ("Russian", "ru"),
            ("Serbian", "sr"),
            ("Slovenian", "sl"),
            ("Spanish", "es"),
            ("Swedish", "sv"),
            ("Turkish", "tr"),
            ("Ukrainian", "uk"),
        ]

        for i in languages:
            self.list.append(
                {
                    "name": str(i[0]),
                    "url": self.language_link % i[1],
                    "image": "languages.png",
                    "action": "movies",
                }
            )
        self.addDirectory(self.list)
        return self.list

    def certifications(self):
        certificates = ["G", "PG", "PG-13", "R", "NC-17"]

        for i in certificates:
            self.list.append(
                {
                    "name": str(i),
                    "url": self.certification_link % str(i),
                    "image": "certificates.png",
                    "action": "movies",
                }
            )
        self.addDirectory(self.list)
        return self.list

    def years(self):
        year = self.datetime.strftime("%Y")
        for i in range(int(year) - 0, 1900, -1):
            self.list.append(
                {
                    "name": str(i),
                    "url": self.year_link % (str(i), str(i)),
                    "image": "years.png",
                    "action": "movies",
                }
            )
        self.addDirectory(self.list)
        return self.list

    def genres(self):
        self.list.append(
            {
                "name": "Akcja",
                "url": "action",
                "image": "action.jpg",
                "action": "movies",
            }
        )
        self.list.append(
            {
                "name": "Przygodowe",
                "url": "adventure",
                "image": "adventure.jpg",
                "action": "movies",
            }
        )
        self.list.append(
            {
                "name": "Animacja",
                "url": "animation",
                "image": "animation.jpg",
                "action": "movies",
            }
        )
        self.list.append(
            {"name": "Anime", "url": "anime", "image": "anime.jpg", "action": "movies"}
        )
        self.list.append(
            {
                "name": "Biograficzny",
                "url": "biography",
                "image": "biography.jpg",
                "action": "movies",
            }
        )
        self.list.append(
            {
                "name": "Komedia",
                "url": "comedy",
                "image": "comedy.jpg",
                "action": "movies",
            }
        )
        self.list.append(
            {
                "name": "Kryminalny",
                "url": "crime",
                "image": "crime.jpg",
                "action": "movies",
            }
        )
        self.list.append(
            {
                "name": "Dokumentalny",
                "url": "documentary",
                "image": "documentary.jpg",
                "action": "movies",
            }
        )
        self.list.append(
            {"name": "Dramat", "url": "drama", "image": "drama.jpg", "action": "movies"}
        )
        self.list.append(
            {
                "name": "Familijny",
                "url": "family",
                "image": "family.jpg",
                "action": "movies",
            }
        )
        self.list.append(
            {
                "name": "Fantasy",
                "url": "fantasy",
                "image": "fantasy.jpg",
                "action": "movies",
            }
        )
        self.list.append(
            {
                "name": "Historyczny",
                "url": "history",
                "image": "history.jpg",
                "action": "movies",
            }
        )
        self.list.append(
            {
                "name": "Horror",
                "url": "horror",
                "image": "horror.jpg",
                "action": "movies",
            }
        )
        self.list.append(
            {
                "name": "Muzyczny",
                "url": "music",
                "image": "music.jpg",
                "action": "movies",
            }
        )
        self.list.append(
            {
                "name": "Musical",
                "url": "musical",
                "image": "musical.jpg",
                "action": "movies",
            }
        )
        self.list.append(
            {
                "name": "Tajemnica",
                "url": "mystery",
                "image": "mystery.jpg",
                "action": "movies",
            }
        )
        self.list.append(
            {
                "name": "Romans",
                "url": "romance",
                "image": "romance.jpg",
                "action": "movies",
            }
        )
        self.list.append(
            {
                "name": "Science Fiction",
                "url": "sci_fi",
                "image": "scifi.jpg",
                "action": "movies",
            }
        )
        self.list.append(
            {"name": "Sport", "url": "sport", "image": "sport.jpg", "action": "movies"}
        )
        self.list.append(
            {
                "name": "Thriller",
                "url": "thriller",
                "image": "thriller.jpg",
                "action": "movies",
            }
        )
        self.list.append(
            {"name": "Wojenny", "url": "war", "image": "war.jpg", "action": "movies"}
        )
        self.list.append(
            {
                "name": "Western",
                "url": "western",
                "image": "western.jpg",
                "action": "movies",
            }
        )
        self.addDirectory(self.list)
        return self.list

    def years_top(self):
        self.list.append(
            {
                "name": "[I]Lata 50[/I] - [B]1950 - 1959[/B]",
                "url": "y50",
                "image": "years.png",
                "action": "movies",
            }
        )
        self.list.append(
            {
                "name": "[I]Lata 60[/I] - [B]1960 - 1969[/B]",
                "url": "y60",
                "image": "years.png",
                "action": "movies",
            }
        )
        self.list.append(
            {
                "name": "[I]Lata 70[/I] - [B]1970 - 1979[/B]",
                "url": "y70",
                "image": "years.png",
                "action": "movies",
            }
        )
        self.list.append(
            {
                "name": "[I]Lata 80[/I] - [B]1980 - 1989[/B]",
                "url": "y80",
                "image": "years.png",
                "action": "movies",
            }
        )
        self.list.append(
            {
                "name": "[I]Lata 90[/I] - [B]1990 - 1999[/B]",
                "url": "y90",
                "image": "years.png",
                "action": "movies",
            }
        )
        self.list.append(
            {
                "name": "[I]Lata 2000[/I] - [B]2000 - 2009[/B]",
                "url": "y2000",
                "image": "years.png",
                "action": "movies",
            }
        )
        self.list.append(
            {
                "name": "[I]Lata 2010[/I] - [B]2010 - 2019[/B]",
                "url": "y2010",
                "image": "years.png",
                "action": "movies",
            }
        )
        self.list.append(
            {
                "name": "[I]Lata 2020[/I] - [B]2020 - dziś[/B]",
                "url": "y2020",
                "image": "years.png",
                "action": "movies",
            }
        )
        self.addDirectory(self.list)
        return self.list

    def my_imdbUserLists(self):
        movielist1 = control.setting("imdb.movielist_name1")
        movielist1_link = control.setting("imdb.movielist_id1")
        if movielist1:
            self.list.append(
                {
                    "name": movielist1,
                    "url": self.imdbUserLists_link % movielist1_link,
                    "image": "imdb.png",
                    "action": "movies",
                }
            )
        movielist2 = control.setting("imdb.movielist_name2")
        movielist2_link = control.setting("imdb.movielist_id2")
        if movielist2:
            self.list.append(
                {
                    "name": movielist2,
                    "url": self.imdbUserLists_link % movielist2_link,
                    "image": "imdb.png",
                    "action": "movies",
                }
            )
        movielist3 = control.setting("imdb.movielist_name3")
        movielist3_link = control.setting("imdb.movielist_id3")
        if movielist3:
            self.list.append(
                {
                    "name": movielist3,
                    "url": self.imdbUserLists_link % movielist3_link,
                    "image": "imdb.png",
                    "action": "movies",
                }
            )
        movielist4 = control.setting("imdb.movielist_name4")
        movielist4_link = control.setting("imdb.movielist_id4")
        if movielist4:
            self.list.append(
                {
                    "name": movielist4,
                    "url": self.imdbUserLists_link % movielist4_link,
                    "image": "imdb.png",
                    "action": "movies",
                }
            )
        movielist5 = control.setting("imdb.movielist_name5")
        movielist5_link = control.setting("imdb.movielist_id5")
        if movielist5:
            self.list.append(
                {
                    "name": movielist5,
                    "url": self.imdbUserLists_link % movielist5_link,
                    "image": "imdb.png",
                    "action": "movies",
                }
            )
        movielist6 = control.setting("imdb.movielist_name6")
        movielist6_link = control.setting("imdb.movielist_id6")
        if movielist6:
            self.list.append(
                {
                    "name": movielist6,
                    "url": self.imdbUserLists_link % movielist6_link,
                    "image": "imdb.png",
                    "action": "movies",
                }
            )
        movielist7 = control.setting("imdb.movielist_name7")
        movielist7_link = control.setting("imdb.movielist_id7")
        if movielist7:
            self.list.append(
                {
                    "name": movielist7,
                    "url": self.imdbUserLists_link % movielist7_link,
                    "image": "imdb.png",
                    "action": "movies",
                }
            )
        movielist8 = control.setting("imdb.movielist_name8")
        movielist8_link = control.setting("imdb.movielist_id8")
        if movielist8:
            self.list.append(
                {
                    "name": movielist8,
                    "url": self.imdbUserLists_link % movielist8_link,
                    "image": "imdb.png",
                    "action": "movies",
                }
            )
        movielist9 = control.setting("imdb.movielist_name9")
        movielist9_link = control.setting("imdb.movielist_id9")
        if movielist9:
            self.list.append(
                {
                    "name": movielist9,
                    "url": self.imdbUserLists_link % movielist9_link,
                    "image": "imdb.png",
                    "action": "movies",
                }
            )
        movielist10 = control.setting("imdb.movielist_name10")
        movielist10_link = control.setting("imdb.movielist_id10")
        if movielist10:
            self.list.append(
                {
                    "name": movielist10,
                    "url": self.imdbUserLists_link % movielist10_link,
                    "image": "imdb.png",
                    "action": "movies",
                }
            )
        self.addDirectory(self.list)
        return self.list

    def awards(self):
        self.list.append(
            {
                "name": "Oscary - najlepszy film",
                "url": "oscarsbestmovie",
                "image": "oscar-winners.png",
                "action": "movies",
            }
        )
        self.list.append(
            {
                "name": "Oscary - najlepszy film - nominowane",
                "url": "oscarsbestmovienom",
                "image": "oscar-winners.png",
                "action": "movies",
            }
        )
        self.list.append(
            {
                "name": "Oscary - najlepszy reżyser",
                "url": "oscarsbestdir",
                "image": "oscar-winners.png",
                "action": "movies",
            }
        )
        self.list.append(
            {
                "name": "Oscary - najlepszy reżyser - nominowane",
                "url": "oscarsbestdirnom",
                "image": "oscar-winners.png",
                "action": "movies",
            }
        )
        self.list.append(
            {
                "name": "Oscary - wszystkie kategorie",
                "url": "oscars",
                "image": "oscar-winners.png",
                "action": "movies",
            }
        )
        self.list.append(
            {
                "name": "Oscary - wszystkie kategorie - nominowane",
                "url": "oscarsnom",
                "image": "oscar-winners.png",
                "action": "movies",
            }
        )
        self.list.append(
            {
                "name": "Złote Maliny",
                "url": "razzie",
                "image": "razzie_winners.png",
                "action": "movies",
            }
        )
        self.list.append(
            {
                "name": "Złote Maliny - nominowane",
                "url": "razzienom",
                "image": "razzie_winners.png",
                "action": "movies",
            }
        )
        self.addDirectory(self.list)
        return self.list

    def companies(self):
        self.list.append(
            {
                "name": "20th Century Fox",
                "url": "thcenturyfox",
                "image": "20thcenturyfox.png",
                "action": "movies",
            }
        )
        self.list.append(
            {
                "name": "DreamWorks",
                "url": "dreamworks",
                "image": "dreamworks.png",
                "action": "movies",
            }
        )
        self.list.append(
            {
                "name": "Netflix",
                "url": "netflix",
                "image": "netflix.png",
                "action": "movies",
            }
        )
        self.list.append(
            {"name": "MGM", "url": "mgm", "image": "mgm.png", "action": "movies"}
        )
        self.list.append(
            {
                "name": "Paramount",
                "url": "paramount",
                "image": "paramount.png",
                "action": "movies",
            }
        )
        self.list.append(
            {"name": "Sony", "url": "sony", "image": "sony.png", "action": "movies"}
        )
        self.list.append(
            {
                "name": "Universal",
                "url": "universal",
                "image": "universal.png",
                "action": "movies",
            }
        )
        self.list.append(
            {
                "name": "Walt Disney",
                "url": "waltdisney",
                "image": "waltdisney.png",
                "action": "movies",
            }
        )
        self.list.append(
            {
                "name": "Warner Bross",
                "url": "warnerbross",
                "image": "warnerbross.png",
                "action": "movies",
            }
        )

        self.addDirectory(self.list)
        return self.list

    def persons(self, url):
        if url == None:
            self.list = cache.get(self.imdb_person_list, 24, self.personlist_link)
        else:
            self.list = cache.get(self.imdb_person_list, 1, url)

        for i in range(0, len(self.list)):
            self.list[i].update({"action": "movies"})
        self.addDirectory(self.list)
        return self.list

    def userlists(self):
        try:
            userlists = []
            if trakt.getTraktCredentialsInfo() == False:
                raise Exception()
            activity = trakt.getActivity()
        except:
            pass

        try:
            if trakt.getTraktCredentialsInfo() == False:
                raise Exception()
            try:
                if activity > cache.timeout(
                    self.trakt_user_list, self.traktlists_link, self.trakt_user
                ):
                    raise Exception()
                userlists += cache.get(
                    self.trakt_user_list, 720, self.traktlists_link, self.trakt_user
                )
            except:
                userlists += cache.get(
                    self.trakt_user_list, 0, self.traktlists_link, self.trakt_user
                )
        except:
            pass
        try:
            self.list = []
            if self.imdb_user == "":
                raise Exception()
            userlists += cache.get(self.imdb_user_list, 0, self.imdblists_link)
        except:
            pass
        try:
            self.list = []
            if trakt.getTraktCredentialsInfo() == False:
                raise Exception()
            try:
                if activity > cache.timeout(
                    self.trakt_user_list, self.traktlikedlists_link, self.trakt_user
                ):
                    raise Exception()
                userlists += cache.get(
                    self.trakt_user_list,
                    720,
                    self.traktlikedlists_link,
                    self.trakt_user,
                )
            except:
                userlists += cache.get(
                    self.trakt_user_list, 0, self.traktlikedlists_link, self.trakt_user
                )
        except:
            pass

        self.list = userlists
        for i in range(0, len(self.list)):
            self.list[i].update({"image": "userlists.png", "action": "movies"})
        self.addDirectory(self.list, queue=True)
        return self.list

    def trakt_list(self, url, user):
        try:
            q = dict(urllib.parse_qsl(urllib.urlsplit(url).query))
            q.update({"extended": "full"})
            q = (urllib.urlencode(q)).replace("%2C", ",")
            u = url.replace("?" + urllib.urlparse(url).query, "") + "?" + q

            result = trakt.getTraktAsJson(u)
            result = convert(result)

            items = []
            for i in result:
                try:
                    items.append(i["movie"])
                except:
                    pass
            if len(items) == 0:
                items = result
        except:
            return

        try:
            q = dict(urllib.parse_qsl(urllib.urlsplit(url).query))
            if not int(q["limit"]) == len(items):
                raise Exception()
            q.update({"page": str(int(q["page"]) + 1)})
            q = (urllib.urlencode(q)).replace("%2C", ",")
            next = url.replace("?" + urllib.urlparse(url).query, "") + "?" + q
            next = next.encode("utf-8")
        except:
            next = ""

        for item in items:
            try:
                title = item["title"]
                title = client.replaceHTMLCodes(title)

                year = item["year"]
                year = re.sub("[^0-9]", "", str(year))
                year_now = self.datetime.strftime("%Y")

                if int(year) > int(year_now):
                    raise Exception()

                imdb = item["ids"]["imdb"]
                if imdb == None or imdb == "":
                    raise Exception()
                imdb = "tt" + re.sub("[^0-9]", "", str(imdb))
                tmdb = str(item.get("ids", {}).get("tmdb", 0))

                try:
                    premiered = item["released"]
                except:
                    premiered = "0"
                try:
                    premiered = re.compile("(\d{4}-\d{2}-\d{2})").findall(premiered)[0]
                except:
                    premiered = "0"

                try:
                    genre = item["genres"]
                except:
                    genre = "0"
                genre = [i.title() for i in genre]
                if genre == []:
                    genre = "0"
                genre = " / ".join(genre)

                try:
                    duration = str(item["runtime"])
                except:
                    duration = "0"
                if duration == None:
                    duration = "0"

                try:
                    rating = str(item["rating"])
                except:
                    rating = "0"
                if rating == None or rating == "0.0":
                    rating = "0"

                try:
                    votes = str(item["votes"])
                except:
                    votes = "0"
                try:
                    votes = str(format(int(votes), ",d"))
                except:
                    pass
                if votes == None:
                    votes = "0"

                try:
                    mpaa = item["certification"]
                except:
                    mpaa = "0"
                if mpaa == None:
                    mpaa = "0"

                try:
                    plot = item["overview"]
                except:
                    plot = "0"
                if plot == None:
                    plot = "0"
                plot = client.replaceHTMLCodes(plot)

                try:
                    tagline = item["tagline"]
                except:
                    tagline = "0"
                if tagline == None:
                    tagline = "0"
                tagline = client.replaceHTMLCodes(tagline)

                self.list.append(
                    {
                        "title": title,
                        "originaltitle": title,
                        "year": year,
                        "premiered": premiered,
                        "genre": genre,
                        "duration": duration,
                        "rating": rating,
                        "votes": votes,
                        "mpaa": mpaa,
                        "plot": plot,
                        "tagline": tagline,
                        "imdb": imdb,
                        "tmdb": tmdb,
                        "tvdb": "0",
                        "poster": "0",
                        "next": next,
                    }
                )
            except:
                pass

        return self.list

    def trakt_user_list(self, url, user):
        try:
            items = trakt.getTraktAsJson(url)
        except:
            pass

        for item in items:
            try:
                try:
                    name = item["list"]["name"]
                except:
                    name = item["name"]
                name = client.replaceHTMLCodes(name)

                try:
                    url = (
                        trakt.slug(item["list"]["user"]["username"]),
                        item["list"]["ids"]["slug"],
                    )
                except:
                    url = ("me", item["ids"]["slug"])
                url = self.traktlist_link % url
                url = url.encode("utf-8")

                self.list.append({"name": name, "url": url, "context": url})
            except:
                pass

        self.list = sorted(self.list, key=lambda k: utils.title_key(k["name"]))
        return self.list

    def imdb_list(self, url):
        try:
            for i in re.findall("date\[(\d+)\]", url):
                url = url.replace(
                    "date[%s]" % i,
                    (self.datetime - datetime.timedelta(days=int(i))).strftime(
                        "%Y-%m-%d"
                    ),
                )

            def imdb_watchlist_id(url):
                return client.parseDOM(
                    client.request(url),
                    "meta",
                    ret="content",
                    attrs={"property": "pageId"},
                )[0]

            if url == self.imdbwatchlist_link:
                url = cache.get(imdb_watchlist_id, 8640, url)
                url = self.imdblist_link % url

            elif url == self.imdbwatchlist2_link:
                url = cache.get(imdb_watchlist_id, 8640, url)
                url = self.imdblist2_link % url

            result = client.request(url)

            result = result.replace("\n", " ")

            items = client.parseDOM(result, "div", attrs={"class": "lister-item .+?"})
            items += client.parseDOM(result, "div", attrs={"class": "list_item.+?"})
        except:
            return

        try:
            next = client.parseDOM(
                result, "a", ret="href", attrs={"class": ".+?ister-page-nex.+?"}
            )

            if len(next) == 0:
                next = client.parseDOM(result, "div", attrs={"class": "pagination"})[0]
                next = zip(
                    client.parseDOM(next, "a", ret="href"), client.parseDOM(next, "a")
                )
                next = [i[0] for i in next if "Next" in i[1]]

            next = url.replace(
                urllib.urlparse(url).query, urllib.urlparse(next[0]).query
            )
            next = client.replaceHTMLCodes(next)
#            next = next.encode("utf-8")
        except:
            next = ""

        for item in items:
            try:
                title = client.parseDOM(item, "a")[1]
                title = client.replaceHTMLCodes(title)
#                title = title.encode("utf-8").decode()

                year = client.parseDOM(
                    item, "span", attrs={"class": "lister-item-year.+?"}
                )
                year += client.parseDOM(item, "span", attrs={"class": "year_type"})
                try:
                    if type(year) == list:
                        year = year[0]
                    year = re.compile("(\d{4})").findall(year)[0]
                except:
                    year = "0"
#                year = year.encode("utf-8")

                if int(year) > int((self.datetime).strftime("%Y")):
                    raise Exception()

                imdb = client.parseDOM(item, "a", ret="href")[0]
                imdb = re.findall("(tt\d*)", imdb)[0]
#                imdb = imdb.encode("utf-8")
                try:
                    poster = client.parseDOM(item, "img", ret="loadlate")[0]
                except:
                    poster = "0"
                if "/nopicture/" in poster:
                    poster = "0"
                poster = re.sub(
                    "(?:_SX|_SY|_UX|_UY|_CR|_AL)(?:\d+|_).+?\.", "_SX500.", poster
                )
                poster = client.replaceHTMLCodes(poster)
#                poster = poster.encode("utf-8")

                try:
                    genre = client.parseDOM(item, "span", attrs={"class": "genre"})[0]
                except:
                    genre = "0"
                genre = " / ".join([i.strip() for i in genre.split(",")])
                if genre == "":
                    genre = "0"
                genre = client.replaceHTMLCodes(genre)
#                genre = genre.encode("utf-8")

                try:
                    duration = re.findall("(\d+?) min(?:s|)", item)[-1]
                except:
                    duration = "0"
#                duration = duration.encode("utf-8")

                rating = "0"
                try:
                    rating = client.parseDOM(
                        item, "span", attrs={"class": "rating-rating"}
                    )[0]
                except:
                    pass
                try:
                    rating = client.parseDOM(rating, "span", attrs={"class": "value"})[
                        0
                    ]
                except:
                    rating = "0"
                try:
                    rating = client.parseDOM(
                        item, "div", ret="data-value", attrs={"class": ".*?imdb-rating"}
                    )[0]
                except:
                    pass
                if rating == "" or rating == "-":
                    rating = "0"
                rating = client.replaceHTMLCodes(rating)
#                rating = rating.encode("utf-8")

                try:
                    votes = client.parseDOM(
                        item, "div", ret="title", attrs={"class": ".*?rating-list"}
                    )[0]
                except:
                    votes = "0"
                try:
                    votes = re.findall("\((.+?) vote(?:s|)\)", votes)[0]
                except:
                    votes = "0"
                if votes == "":
                    votes = "0"
                votes = client.replaceHTMLCodes(votes)
#                votes = votes.encode("utf-8")

                try:
                    mpaa = client.parseDOM(
                        item, "span", attrs={"class": "certificate"}
                    )[0]
                except:
                    mpaa = "0"
                if mpaa == "" or mpaa == "NOT_RATED":
                    mpaa = "0"
                mpaa = mpaa.replace("_", "-")
                mpaa = client.replaceHTMLCodes(mpaa)
#                mpaa = mpaa.encode("utf-8")

                try:
                    director = re.findall("Director(?:s|):(.+?)(?:\||</div>)", item)[0]
                except:
                    director = "0"
                director = client.parseDOM(director, "a")
                director = " / ".join(director)
                if director == "":
                    director = "0"
                director = client.replaceHTMLCodes(director)
#                director = director.encode("utf-8")

                try:
                    cast = re.findall("Stars(?:s|):(.+?)(?:\||</div>)", item)[0]
                except:
                    cast = "0"
                cast = client.replaceHTMLCodes(cast)
                cast = cast.encode("utf-8")
                cast = client.parseDOM(cast, "a")
                if cast == []:
                    cast = "0"

                plot = "0"
                try:
                    plot = client.parseDOM(item, "p", attrs={"class": "text-muted"})[0]
                except:
                    pass
                try:
                    plot = client.parseDOM(
                        item, "div", attrs={"class": "item_description"}
                    )[0]
                except:
                    pass
                plot = plot.rsplit("<span>", 1)[0].strip()
                plot = re.sub("<.+?>|</.+?>", "", plot)
                if plot == "":
                    plot = "0"
                plot = client.replaceHTMLCodes(plot)
#                plot = plot.encode("utf-8")

                self.list.append(
                    {
                        "title": title,
                        "originaltitle": title,
                        "year": year,
                        "genre": genre,
                        "duration": duration,
                        "rating": rating,
                        "votes": votes,
                        "mpaa": mpaa,
                        "director": director,
                        "cast": cast,
                        "plot": plot,
                        "tagline": "0",
                        "imdb": imdb,
                        "tmdb": "0",
                        "tvdb": "0",
                        "poster": poster,
                        "next": next,
                    }
                )
            except Exception as e:
                print(e)
                pass

        return self.list

    def imdb_person_list(self, url):
        try:
            result = client.request(url)
            items = client.parseDOM(result, "div", attrs={"class": ".+?etail"})
        except:
            return

        for item in items:
            try:
                name = client.parseDOM(item, "img", ret="alt")[0]
#                name = name.encode("utf-8")

                url = client.parseDOM(item, "a", ret="href")[0]
                url = re.findall("(nm\d*)", url, re.I)[0]
                url = self.person_link % url
                url = client.replaceHTMLCodes(url)
#                url = url.encode("utf-8")

                image = client.parseDOM(item, "img", ret="src")[0]
                # if not ('._SX' in image or '._SY' in image): raise Exception()
                image = re.sub(
                    "(?:_SX|_SY|_UX|_UY|_CR|_AL)(?:\d+|_).+?\.", "_SX500.", image
                )
                image = client.replaceHTMLCodes(image)
#                image = image.encode("utf-8")

                self.list.append({"name": name, "url": url, "image": image})
            except:
                pass

        return self.list

    def imdb_user_list(self, url):
        try:
            result = client.request(url)
            items = client.parseDOM(
                result, "li", attrs={"class": "ipl-zebra-list__item user-list"}
            )
        except:
            pass

        for item in items:
            try:
                name = client.parseDOM(item, "a")[0]
                name = client.replaceHTMLCodes(name)
                name = name.encode("utf-8")

                url = client.parseDOM(item, "a", ret="href")[0]
                url = url.split("/list/", 1)[-1].strip("/")
                url = self.imdblist_link % url
                url = client.replaceHTMLCodes(url)
                url = url.encode("utf-8")

                self.list.append({"name": name, "url": url, "context": url})
            except:
                pass

        self.list = sorted(self.list, key=lambda k: utils.title_key(k["name"]))
        return self.list

    def worker(self, level=1):
        self.meta = []
        total = len(self.list)

        for i in range(0, total):
            self.list[i].update({"metacache": False})

        self.list = metacache.fetch(self.list, self.lang, self.user)
        import threading

        for r in range(0, total, 40):
            threads = []
            for i in range(r, r + 40):
                if i <= total:
                    threads.append(threading.Thread(target=self.super_info, args=(i,)))

            [i.start() for i in threads]
            [i.join() for i in threads]

            if self.meta:
                metacache.insert(self.meta)

        self.list = [i for i in self.list if not i["imdb"] == "0"]

    def super_info(self, i):
        try:
            if self.list[i]['metacache'] == True: return
            imdb = self.list[i]['imdb'] if 'imdb' in self.list[i] else '0'
            tmdb = self.list[i]['tmdb'] if 'tmdb' in self.list[i] else '0'
            list_title = self.list[i]['title']

            if tmdb == '0' and not imdb == '0':
                try:
                    url = self.tmdb_by_imdb % imdb
                    result = self.session.get(url, timeout=16).json()
                    id = result['movie_results'][0]
                    tmdb = id['id']
                    if not tmdb: tmdb = '0'
                    else: tmdb = str(tmdb)
                except:
                    pass

            # if tmdb == '0':
                # try:
                    # url = self.tm_search_link % (urllib_parse.quote(list_title)) + '&year=' + self.list[i]['year']
                    # result = self.session.get(url, timeout=16).json()
                    # results = result['results']
                    # movie = [r for r in results if cleantitle.get(r.get('name')) == cleantitle.get(list_title)][0]# and re.findall('(\d{4})', r.get('first_air_date'))[0] == self.list[i]['year']][0]
                    # tmdb = movie.get('id')
                    # if not tmdb: tmdb = '0'
                    # else: tmdb = str(tmdb)
                # except:
                    # pass

            id = tmdb if not tmdb == '0' else imdb
            if id == '0': raise Exception()

            en_url = self.tmdb_api_link % (id)# + ',images'
            f_url = en_url + ',translations'#,images&include_image_language=en,%s,null' % self.lang
            url = en_url if self.lang == 'en' else f_url
            #log_utils.log('tmdb_url: ' + url)

            r = self.session.get(url, timeout=10)
            r.raise_for_status()
            r.encoding = 'utf-8'
            item = r.json()
            #log_utils.log('tmdb_item: ' + repr(item))

            if imdb == '0':
                try:
                    imdb = item['external_ids']['imdb_id']
                    if not imdb: imdb = '0'
                except:
                    imdb = '0'

            original_language = item.get('original_language', '')

            if self.lang == 'en':
                en_trans_item = None
            else:
                try:
                    translations = item['translations']['translations']
                    en_trans_item = [x['data'] for x in translations if x['iso_639_1'] == 'en'][0]
                except:
                    en_trans_item = {}

            name = item.get('title', '')
            original_name = item.get('original_title', '')
            en_trans_name = en_trans_item.get('title', '') if not self.lang == 'en' else None
            #log_utils.log('self_lang: %s | original_language: %s | list_title: %s | name: %s | original_name: %s | en_trans_name: %s' % (self.lang, original_language, list_title, name, original_name, en_trans_name))

            if self.lang == 'en':
                originaltitle = title = name
            elif self.lang == 'pl' and original_language != 'pl' and en_trans_name:
                originaltitle = title = en_trans_name
            else:
                originaltitle = en_trans_name or original_name
                if original_language == self.lang:
                    title = name
                else:
                    title = name #or en_trans_name
            try:
                plot = None
                tagline = None
                translations_trakt = trakt.getMovieTranslation(item['imdb_id'], self.lang, full=True)
                title = translations_trakt['title']
                plot = translations_trakt['overview']
                tagline = translations_trakt['tagline']
            except:
                pass
            if not originaltitle: originaltitle = list_title
            if not title: title = list_title

            if not plot: plot = item.get('overview') or self.list[i]['plot']

            if not tagline: tagline = item.get('tagline') or '0'

            if not self.lang == 'en':
                if plot == '0':
                    en_plot = en_trans_item.get('overview', '')
                    if en_plot: plot = en_plot

                if tagline == '0':
                    en_tagline = en_trans_item.get('tagline', '')
                    if en_tagline: tagline = en_tagline

            premiered = item.get('release_date') or '0'

            try: _year = re.findall('(\d{4})', premiered)[0]
            except: _year = ''
            if not _year : _year = '0'
            year = self.list[i]['year'] if not self.list[i]['year'] == '0' else _year

            status = item.get('status') or '0'

            try: studio = item['production_companies'][0]['name']
            except: studio = ''
            if not studio: studio = '0'

            try:
                genre = item['genres']
                genre = [d['name'] for d in genre]
                genre = ' / '.join(genre)
            except:
                genre = ''
            if not genre: genre = '0'

            try:
                country = item['production_countries']
                country = [c['name'] for c in country]
                country = ' / '.join(country)
            except:
                country = ''
            if not country: country = '0'

            try:
                duration = str(item['runtime'])
            except:
                duration = ''
            if not duration: duration = '0'

            castwiththumb = []
            try:
                c = item['credits']['cast'][:30]
                for person in c:
                    _icon = person['profile_path']
                    icon = self.tm_img_link % ('185', _icon) if _icon else ''
                    castwiththumb.append({'name': person['name'], 'role': person['character'], 'thumbnail': icon})
            except:
                pass
            if not castwiththumb: castwiththumb = '0'

            try:
                crew = item['credits']['crew']
                director = ', '.join([d['name'] for d in [x for x in crew if x['job'] == 'Director']])
                writer = ', '.join([w['name'] for w in [y for y in crew if y['job'] in ['Writer', 'Screenplay', 'Author', 'Novel']]])
            except:
                director = writer = '0'

            my_language_order = ['pl', 'en', '00', ""]
            language_order = {key: i for i, key in enumerate(my_language_order)}
            posters_language = {}
            fanarts_language = {}
            banner_language = {}
            clearlogo_language = {}
            clearart_language = {}
            landscape_language = {}
            discart_language = {}
            poster1 = self.list[i]['poster']
            poster2 = None
            _fanart2 = None

            try:
                poster2_url = self.tmdb_arts % tmdb
                r2 = self.session.get(poster2_url, timeout=10)
                r2.raise_for_status()
                r2.encoding = 'utf-8'
                art = r2.json()
                try:
                    _poster2 = art['posters']
                    _poster2 = [x for x in _poster2 if x.get('iso_639_1') == self.lang][::-1] + [x for x in _poster2 if x.get('iso_639_1') == 'en'][::-1] + [x for x in _poster2 if x.get('lang') in ['00', '']][::-1]
                    _poster2 = sorted(_poster2,
                                          key=lambda d: (language_order[d["iso_639_1"]], -d["vote_average"]))
                    posters_language.update({"tmdb": _poster2[0]["iso_639_1"]})
                    _poster2 = _poster2[0]['file_path']
                    if _poster2: poster2 = "https://image.tmdb.org/t/p/w500" + _poster2
                except:
                    poster2 = None
                    pass
                try:
                    _fanart2 = art['backdrops']
                    _fanart2 = [x for x in _fanart2 if x.get('iso_639_1') == self.lang][::-1] + [x for x in _fanart2 if x.get('iso_639_1') == 'en'][::-1] + [x for x in _fanart2 if x.get('lang') in ['00', '']][::-1]
                    _fanart2 = sorted(_fanart2,
                                          key=lambda d: (language_order[d["iso_639_1"]], -d["vote_average"]))
                    fanarts_language.update({"tmdb": _fanart2[0]["iso_639_1"]})
                    _fanart2 = _fanart2[0]['file_path']
                    if _fanart2: _fanart2 = "https://image.tmdb.org/t/p/w1280" + _fanart2
                except:
                    _fanart2 = None
                    pass
            except:
                poster2 = None
                pass

            fanart_path = item.get('backdrop_path')
            if fanart_path:
                fanart1 = self.tm_img_link % ('1280', fanart_path)
            else:
                fanart1 = '0'

            poster3 = fanart3 = None
            banner = clearlogo = clearart = landscape = discart = '0'
#            if self.hq_artwork == 'true' and not imdb == '0':# and not self.fanart_tv_user == '':

            try:
                #if self.fanart_tv_user == '': raise Exception()
                r2 = self.session.get(self.fanart_tv_art_link % imdb, headers=self.fanart_tv_headers, timeout=10)
                r2.raise_for_status()
                r2.encoding = 'utf-8'
                art = r2.json()

                try:
                    _poster3 = art['movieposter']
                    _poster3 = [x for x in _poster3 if x["lang"] == ("en" or "pl" or "00" or "")]
                    _poster3 = [x for x in _poster3 if x.get('lang') == self.lang][::-1] + [x for x in _poster3 if x.get('lang') == 'en'][::-1] + [x for x in _poster3 if x.get('lang') in ['00', '']][::-1]
                    _poster3 = sorted(_poster3,
                                          key=lambda d: (language_order[d["lang"]], d["likes"]))
                    posters_language.update({"fanart": _poster3[0]["lang"]})
                    _poster3 = _poster3[0]['url']
                    if _poster3: poster3 = _poster3
                except:
                    pass

                try:
                    if 'moviebackground' in art: _fanart3 = art['moviebackground']
                    else: _fanart3 = art['moviethumb']
                    _fanart3 = [x for x in _fanart3 if x.get('lang') == self.lang][::-1] + [x for x in _fanart3 if x.get('lang') == 'en'][::-1] + [x for x in _fanart3 if x.get('lang') in ['00', '']][::-1]
                    _fanart3 = sorted(_fanart3,
                                          key=lambda d: (language_order[d["lang"]], d["likes"]))
                    fanarts_language.update({"fanart": _fanart3[0]["lang"]})
                    _fanart3 = _fanart3[0]['url']
                    if _fanart3: fanart3 = _fanart3
                except:
                    pass

                try:
                    _banner = art['moviebanner']
                    _banner = [x for x in _banner if x.get('lang') == self.lang][::-1] + [x for x in _banner if x.get('lang') == 'en'][::-1] + [x for x in _banner if x.get('lang') in ['00', '']][::-1]
                    _banner = sorted(_banner,
                                          key=lambda d: (language_order[d["lang"]], d["likes"]))
                    banner_language.update({"fanart": _banner[0]["lang"]})
                    _banner = _banner[0]['url']
                    if _banner: banner = _banner
                except:
                    pass

                try:
                    if 'hdmovielogo' in art: _clearlogo = art['hdmovielogo']
                    else: _clearlogo = art['clearlogo']
                    _clearlogo = [x for x in _clearlogo if x.get('lang') == self.lang][::-1] + [x for x in _clearlogo if x.get('lang') == 'en'][::-1] + [x for x in _clearlogo if x.get('lang') in ['00', '']][::-1]
                    _clearlogo = sorted(_clearlogo,
                                          key=lambda d: (language_order[d["lang"]], d["likes"]))
                    clearlogo_language.update({"fanart": _clearlogo[0]["lang"]})
                    _clearlogo = _clearlogo[0]['url']
                    if _clearlogo: clearlogo = _clearlogo
                except:
                    pass

                try:
                    if 'hdmovieclearart' in art: _clearart = art['hdmovieclearart']
                    else: _clearart = art['clearart']
                    _clearart = [x for x in _clearart if x.get('lang') == self.lang][::-1] + [x for x in _clearart if x.get('lang') == 'en'][::-1] + [x for x in _clearart if x.get('lang') in ['00', '']][::-1]
                    _clearart = sorted(_clearart,
                                          key=lambda d: (language_order[d["lang"]], d["likes"]))
                    clearart_language.update({"fanart": _clearart[0]["lang"]})
                    _clearart = _clearart[0]['url']
                    if _clearart: clearart = _clearart
                except:
                    pass

                try:
                    if 'moviethumb' in art: _landscape = art['moviethumb']
                    else: _landscape = art['moviebackground']
                    _landscape = [x for x in _landscape if x.get('lang') == self.lang][::-1] + [x for x in _landscape if x.get('lang') == 'en'][::-1] + [x for x in _landscape if x.get('lang') in ['00', '']][::-1]
                    _landscape = sorted(_landscape,
                                          key=lambda d: (language_order[d["lang"]], d["likes"]))
                    landscape_language.update({"fanart": _landscape[0]["lang"]})
                    _landscape = _landscape[0]['url']
                    if _landscape: landscape = _landscape
                except:
                    pass

                try:
                    if 'moviedisc' in art: _discart = art['moviedisc']
                    _discart = [x for x in _discart if x.get('lang') == self.lang][::-1] + [x for x in _discart if x.get('lang') == 'en'][::-1] + [x for x in _discart if x.get('lang') in ['00', '']][::-1]
                    _discart = sorted(_discart,
                                          key=lambda d: (language_order[d["lang"]], d["likes"]))
                    discart_language.update({"fanart": _discart[0]["lang"]})
                    _discart = _discart[0]['url']
                    if _discart: discart = _discart
                except:
                    pass
            except:
                #log_utils.log('fanart.tv art fail', 1)
                pass

            if "tmdb" in posters_language.keys() and posters_language["tmdb"] == "pl":
                poster = poster2
            elif "fanart" in posters_language.keys() and posters_language["fanart"] == "pl":
                poster = poster3
            else:
                poster = poster2 or poster3 or poster1
            fanart = fanart1 or fanart2 or fanart3

            #log_utils.log('title: ' + title + ' - poster: ' + repr(poster))
            providers = ''
            try:
                r3 = self.session.get(self.tmdb_providers % tmdb, timeout=10)
                r3.raise_for_status()
                r3.encoding = 'utf-8'
                provider = r3.json()

                providerspage = provider['results'][self.lang.upper()]['link']
                providers_list = [i['provider_name'] for i in provider['results'][self.lang.upper()]['flatrate']]
                providers = {'link': providerspage, 'provider_list': providers_list}
            except:
                pass

            item = {'title': title, 'originaltitle': originaltitle, 'label': title, 'year': year, 'imdb': imdb, 'tmdb': tmdb, 'poster': poster, 'banner': banner, 'fanart': fanart,
                    'clearlogo': clearlogo, 'clearart': clearart, 'landscape': landscape, 'discart': discart, 'premiered': premiered, 'genre': genre, 'duration': duration,
                    'director': director, 'writer': writer, 'castwiththumb': castwiththumb, 'plot': plot, 'tagline': tagline, 'status': status, 'studio': studio, 'country': country,
                    'providers': providers
            }
            item = dict((k,v) for k, v in item.items() if not v == '0')
            self.list[i].update(item)

            meta = {'imdb': imdb, 'tmdb': tmdb, 'tvdb': '0', 'lang': self.lang, 'user': self.user, 'item': item}
            self.meta.append(meta)
        except:
#            log_utils.log('superinfo_fail', 'indexer') #do poprawy po update log
            pass


    def movieDirectory(self, items):
        if items == None or len(items) == 0:
            control.idle()
            sys.exit()

        sysaddon = sys.argv[0]

        syshandle = int(sys.argv[1])

        addonPoster, addonBanner = control.addonPoster(), control.addonBanner()

        addonFanart, settingFanart = control.addonFanart(), control.setting("fanart")

        traktCredentials = trakt.getTraktCredentialsInfo()

        try:
            isOld = False
            control.item().getArt("type")
        except:
            isOld = True

        isPlayable = (
            "true"
            if not "plugin" in control.infoLabel("Container.PluginName")
            else "false"
        )

        indicators = (
            playcount.getMovieIndicators(refresh=True)
            if action == "movies"
            else playcount.getMovieIndicators()
        )

        playbackMenu = (
            control.lang(32063).encode("utf-8")
            if control.setting("hosts.mode") == "2"
            else control.lang(32064).encode("utf-8")
        )

        watchedMenu = (
            control.lang(32068).encode("utf-8")
            if trakt.getTraktIndicatorsInfo() == True
            else control.lang(32066).encode("utf-8")
        )

        unwatchedMenu = (
            control.lang(32069).encode("utf-8")
            if trakt.getTraktIndicatorsInfo() == True
            else control.lang(32067).encode("utf-8")
        )

        queueMenu = control.lang(32065).encode("utf-8")

        traktManagerMenu = control.lang(32070).encode("utf-8")

        nextMenu = control.lang(32053).encode("utf-8")

        addToLibrary = control.lang(32551).encode("utf-8")

        for i in items:
            try:
                label = "%s (%s)" % (i["label"], i["year"])
                imdb, tmdb, title, year = (
                    i["imdb"],
                    i["tmdb"],
                    i["originaltitle"],
                    i["year"],
                )
                sysname = urllib.quote_plus("%s (%s)" % (title, year))
                systitle = urllib.quote_plus(title)
                meta = dict((k, v) for k, v in i.items() if not v == "0")
                meta.update({'imdbnumber': imdb, 'code': tmdb})
#                meta.update({"code": imdb, "imdbnumber": imdb, "imdb_id": imdb})
#                meta.update({"tmdb_id": tmdb})
                meta.update({"mediatype": "movie"})
                meta.update(
                    {
                        "trailer": "%s?action=trailer&name=%s"
                        % (sysaddon, urllib.quote_plus(label))
                    }
                )
                # meta.update({'trailer': 'plugin://script.extendedinfo/?info=playtrailer&&id=%s' % imdb})
                if not "duration" in i:
                    meta.update({"duration": "120"})
                elif i["duration"] == "0":
                    meta.update({"duration": "120"})
                try:
                    meta.update({"duration": str(int(meta["duration"]) * 60)})
                except:
                    pass
                # try:
                #     meta.update({"genre": cleangenre.lang(meta["genre"], self.lang)})
                # except:
                #     pass

                poster = [
                    i[x]
                    for x in ["poster3", "poster", "poster2"]
                    if i.get(x, "0") != "0"
                ]
                poster = poster[0] if poster else addonPoster
                meta.update({"poster": poster})
                meta = convert(meta)
                sysmeta = urllib.quote_plus(json.dumps(meta))

                url = "%s?action=play&title=%s&year=%s&imdb=%s&meta=%s&t=%s" % (
                    sysaddon,
                    systitle,
                    year,
                    imdb,
                    sysmeta,
                    self.systime,
                )
                sysurl = urllib.quote_plus(url)

                path = "%s?action=play&title=%s&year=%s&imdb=%s" % (
                    sysaddon,
                    systitle,
                    year,
                    imdb,
                )

                cm = []
                cm.append(
                    (
                        "Znajdź podobne",
                        "ActivateWindow(10025,%s?action=movies&url=https://api.trakt.tv/movies/%s/related,return)"
                        % (sysaddon, imdb),
                    )
                )
                cm.append((queueMenu, "RunPlugin(%s?action=queueItem)" % sysaddon))

                try:
                    overlay = int(playcount.getMovieOverlay(indicators, imdb))
                    if overlay == 7:
                        cm.append(
                            (
                                unwatchedMenu,
                                "RunPlugin(%s?action=moviePlaycount&imdb=%s&query=6)"
                                % (sysaddon, imdb),
                            )
                        )
                        meta.update({"playcount": 1, "overlay": 7})
                    else:
                        cm.append(
                            (
                                watchedMenu,
                                "RunPlugin(%s?action=moviePlaycount&imdb=%s&query=7)"
                                % (sysaddon, imdb),
                            )
                        )
                        meta.update({"playcount": 0, "overlay": 6})
                except:
                    pass

                if traktCredentials == True:
                    cm.append(
                        (
                            traktManagerMenu,
                            "RunPlugin(%s?action=traktManager&name=%s&imdb=%s&content=movie)"
                            % (sysaddon, sysname, imdb),
                        )
                    )

                cm.append(
                    (
                        playbackMenu,
                        "RunPlugin(%s?action=alterSources&url=%s&meta=%s)"
                        % (sysaddon, sysurl, sysmeta),
                    )
                )

                if isOld == True:
                    cm.append((control.lang2(19033), "Action(Info)"))

                cm.append(
                    (
                        addToLibrary,
                        "RunPlugin(%s?action=movieToLibrary&name=%s&title=%s&year=%s&imdb=%s&tmdb=%s)"
                        % (sysaddon, sysname, systitle, year, imdb, tmdb),
                    )
                )

                item = control.item(label=label)

                art = {}
                art.update({"icon": poster, "thum": poster, "poster": poster})

                fanart = i['fanart'] if 'fanart' in i and not i['fanart'] == '0' else addonFanart

#                if self.settingFanart == 'true':
                art.update({'fanart': fanart})
#                else:
#                    art.update({'fanart': addonFanart})

                if 'banner' in i and not i['banner'] == '0':
                    art.update({'banner': i['banner']})
                else:
                    art.update({'banner': addonBanner})

                if 'clearlogo' in i and not i['clearlogo'] == '0':
                    art.update({'clearlogo': i['clearlogo']})

                if 'clearart' in i and not i['clearart'] == '0':
                    art.update({'clearart': i['clearart']})

                if 'landscape' in i and not i['landscape'] == '0':
                    landscape = i['landscape']
                else:
                    landscape = fanart
                art.update({'landscape': landscape})

                if 'discart' in i and not i['discart'] == '0':
                    art.update({'discart': i['discart']})

#                meta.pop("imdb", None)
#                meta.pop("tmdb_id", None)
#                meta.pop("imdb_id", None)
#                meta.pop("poster", None)
#                meta.pop("clearlogo", None)
#                meta.pop("clearart", None)
#                meta.pop("fanart", None)
#                meta.pop("fanart3", None)
#                meta.pop("imdb", None)
#                meta.pop("tmdb", None)
#                meta.pop("metacache", None)
#                meta.pop("poster2", None)
#                meta.pop("poster3", None)
#                meta.pop("banner", None)
#                meta.pop("next", None)

                item.setArt(art)
                item.addContextMenuItems(cm)
                item.setProperty("IsPlayable", isPlayable)
                castwiththumb = i.get('castwiththumb')
                item.setCast(castwiththumb)
                item.setInfo(type='Video', infoLabels = control.metadataClean(meta))
                item.setProperty('imdb_id', imdb)
                item.setProperty('tmdb_id', tmdb)
                try: item.setUniqueIDs({'imdb': imdb, 'tmdb': tmdb})
                except: pass


                video_streaminfo = {"codec": "h264"}
                item.addStreamInfo("Video", video_streaminfo)

                control.addItem(handle=syshandle, url=url, listitem=item, isFolder=True)
            except Exception as e:
                print(e)
                pass

        try:
            url = items[0]["next"]
            if url == "":
                raise Exception()

            icon = control.addonNext()
            url = "%s?action=moviePage&url=%s" % (sysaddon, urllib.quote_plus(url))

            item = control.item(label=nextMenu)

            item.setArt({'icon': icon, 'thumb': icon, 'poster': icon, 'banner': icon, 'fanart': addonFanart})

            control.addItem(handle=syshandle, url=url, listitem=item, isFolder=True)
        except:
            pass

        control.content(syshandle, "movies")
        control.directory(syshandle, cacheToDisc=True)
        views.setView("movies", {"skin.estuary": 55, "skin.confluence": 500})

    def addDirectory(self, items, queue=False):
        if items == None or len(items) == 0:
            control.idle()
            sys.exit()

        sysaddon = sys.argv[0]

        syshandle = int(sys.argv[1])

        addonFanart, addonThumb, artPath = (
            control.addonFanart(),
            control.addonThumb(),
            control.artPath(),
        )

        queueMenu = control.lang(32065).encode("utf-8")

        playRandom = control.lang(32535).encode("utf-8")

        addToLibrary = control.lang(32551).encode("utf-8")

        for i in items:
            try:
                name = i["name"]

                plot = i.get('plot') or '[CR]'

                if i["image"].startswith("http"):
                    thumb = i["image"]
                elif not artPath == None:
                    thumb = os.path.join(artPath, i["image"])
                else:
                    thumb = addonThumb

                url = "%s?action=%s" % (sysaddon, i["action"])
                try:
                    url += "&url=%s" % urllib.quote_plus(i["url"])
                except:
                    pass

                cm = []

                cm.append(
                    (
                        playRandom,
                        "RunPlugin(%s?action=random&rtype=movie&url=%s)"
                        % (sysaddon, urllib.quote_plus(i["url"])),
                    )
                )

                if queue == True:
                    cm.append((queueMenu, "RunPlugin(%s?action=queueItem)" % sysaddon))

                try:
                    cm.append(
                        (
                            addToLibrary,
                            "RunPlugin(%s?action=moviesToLibrary&url=%s)"
                            % (sysaddon, urllib.quote_plus(i["context"])),
                        )
                    )
                except:
                    pass

                item = control.item(label=name)

                item.setArt({'icon': thumb, 'thumb': thumb, 'poster': thumb, 'fanart': addonFanart})
                item.setInfo(type='video', infoLabels={'plot': plot})

                item.addContextMenuItems(cm)

                control.addItem(handle=syshandle, url=url, listitem=item, isFolder=True)
            except:
                pass

        control.content(syshandle, "addons")
        control.directory(syshandle, cacheToDisc=True)
