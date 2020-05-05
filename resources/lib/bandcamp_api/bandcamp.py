from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
from builtins import *

import requests
import json
from html.parser import HTMLParser
import time


class Band:
    def __init__(self, band_id, band_name=""):
        self.band_name = band_name
        self.band_id = str(band_id)

    def __eq__(self, other):
        if type(other) is type(self):
            return self.band_id == other.band_id
        else:
            return False

    def __hash__(self):
        return hash(self.band_id)


class Album:
    def __init__(self, album_id, album_name, art_id):
        self.album_name = album_name
        self.art_id = art_id
        self.album_id = album_id

    def get_art_img(self, quality=9):
        return "https://f4.bcbits.com/img/a0{art_id}_{quality}.jpg".format(art_id=self.art_id, quality=quality)


class Track:
    def __init__(self, track_name, file, duration, number=0):
        self.track_name = track_name
        self.file = file
        self.duration = duration
        self.number = number


class _DataBlobParser(HTMLParser):
    data_blob = None

    def handle_starttag(self, tag, attrs):
        for attr in attrs:
            if attr[0] == "data-blob":
                data_html = attr[1]
                self.data_blob = json.loads(data_html)


class _PlayerDataParser(HTMLParser):
    player_data = None

    def handle_data(self, data):
        if "playerdata" in data:
            end = data.index('};') + 1
            player_data = data[26:end]
            self.player_data = json.loads(player_data)


class Bandcamp:

    def __init__(self, user_name):
        self.data_blob = None
        if user_name is None:
            self.user_name = ""
        else:
            self.user_name = user_name

    @staticmethod
    def discover(genre="all", sub_genre="any", slice="best", page=0):
        url = "https://bandcamp.com/api/discover/3/get_web?g={genre}&t={sub_genre}&s={slice}&p={page}&f=all" \
            .format(genre=genre, sub_genre=sub_genre, slice=slice, page=page)
        request = requests.get(url)
        items = json.loads(request.text)['items']
        discover_list = {}
        for item in items:
            track = Track(item['featured_track']['title'], item['featured_track']['file']['mp3-128'],
                          item['featured_track']['duration'])
            album = Album(album_id=item['id'], album_name=item['primary_text'], art_id=item['art_id'])
            band = Band(band_id=item['band_id'], band_name=item['secondary_text'])
            discover_list[band] = {album: [track]}
        print("got", genre, sub_genre, slice)
        return discover_list

    def get_fan_id(self):
        return self._get_data_blob()['fan_data']['fan_id']

    def get_genres(self):
        return self._get_data_blob()['signup_params']['genres']

    def get_subgenres(self):
        return self._get_data_blob()['signup_params']['subgenres']

    def get_collection(self, fan_id, count=1000):
        url = "https://bandcamp.com/api/fancollection/1/collection_items"
        token = self._get_token()
        body = '{{"fan_id": "{fan_id}", "older_than_token": "{token}", "count":"{count}"}}' \
            .format(fan_id=fan_id, token=token, count=count)
        x = requests.post(url, data=body)
        items = json.loads(x.text)['items']
        bands = {}
        for item in items:
            album = Album(album_id=item['item_id'], album_name=item['item_title'], art_id=item['item_art_id'])
            band = Band(band_id=item['band_id'], band_name=item['band_name'])
            if band not in bands:
                bands[band] = {}
            bands[band].update({album: [None]})
        return bands

    def get_album(self, album_id):
        url = "https://bandcamp.com/EmbeddedPlayer/album={album_id}".format(album_id=album_id)
        request = requests.get(url)
        parser = _PlayerDataParser()
        content = request.text
        parser.feed(content)
        player_data = parser.player_data
        track_list = []
        for track in player_data['tracks']:
            track_list.append(
                Track(track['title'], track['file']['mp3-128'], track['duration'], number=track['tracknum'] + 1))
        album = Album(album_id, player_data['album_title'], player_data['album_art_id'])
        return album, track_list

    @staticmethod
    def _get_token():
        return str(int(time.time())) + "::FOO::"

    def _get_data_blob(self):
        if self.data_blob is None:
            url = "https://bandcamp.com/{user_name}".format(user_name=self.user_name)
            request = requests.get(url)
            parser = _DataBlobParser()
            content = request.content.decode('utf-8')
            parser.feed(content)
            self.data_blob = parser.data_blob
        return self.data_blob
