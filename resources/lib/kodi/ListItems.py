import sys

import xbmcgui
from future.standard_library import install_aliases

install_aliases()
from urllib.parse import urlencode


def _build_url(query):
    base_url = sys.argv[0]
    return base_url + '?' + urlencode(query)


def get_root_items(username):
    items = []
    # discover menu
    li = xbmcgui.ListItem(label='discover')
    url = _build_url({'mode': 'list_discover'})
    items.append((url, li, True))
    # collection menu
    # don't add if not configured
    if username == "":
        li = xbmcgui.ListItem(label='add username to access collection')
        url = _build_url({'mode': 'settings'})
        items.append((url, li, True))
    else:
        li = xbmcgui.ListItem(label='collection')
        url = _build_url({'mode': 'list_collection'})
        items.append((url, li, True))
    # search
    li = xbmcgui.ListItem(label="Search")
    url = _build_url({'mode': 'search', 'action': 'new'})
    items.append((url, li, True))
    return items


def get_album_items(albums):
    items = []
    for album in albums:
        li = xbmcgui.ListItem(label=album.album_name)
        url = _build_url({'mode': 'list_songs', 'album_id': album.album_id, 'item_type': album.item_type})
        li.setArt({'thumb': album.get_art_img(), 'fanart': album.get_art_img()})
        items.append((url, li, True))
    return items


def get_genre_items(genres):
    items = []
    li = xbmcgui.ListItem(label='all')
    url = _build_url({'mode': 'list_subgenre_songs', 'category': 'all', 'subcategory': 'all'})
    items.append((url, li, True))
    for genre in genres:
        li = xbmcgui.ListItem(label=genre['name'])
        url = _build_url({'mode': 'list_subgenre', 'category': genre['value']})
        items.append((url, li, True))
    return items


def get_subgenre_items(genre, subgenres):
    items = []
    li = xbmcgui.ListItem(label='all ' + genre)
    url = _build_url({'mode': 'list_subgenre_songs', 'category': genre, 'subcategory': 'all'})
    items.append((url, li, True))
    for subgenre in subgenres[genre]:
        li = xbmcgui.ListItem(label=subgenre['name'])
        url = _build_url({'mode': 'list_subgenre_songs', 'category': genre, 'subcategory': subgenre['value']})
        items.append((url, li, True))
    return items


def get_track_items(band, album, tracks):
    items = []
    for track in tracks:
        if track.number is None:
            title = u"{band} - {track}".format(band=band.band_name, track=track.track_name)
        else:
            title = u"{number}. {track}".format(number=track.number, track=track.track_name)
        li = xbmcgui.ListItem(label=title)
        li.setInfo('music', {'duration': int(track.duration), 'album': album.album_name, 'genre': album.genre,
                             'mediatype': 'song', 'tracknumber': track.number, 'title': track.track_name})
        li.setArt({'thumb': album.get_art_img(), 'fanart': album.get_art_img()})
        li.setProperty('IsPlayable', 'true')
        url = _build_url({'mode': 'stream', 'url': track.file, 'title': title})

        album_url = _build_url({'mode': 'list_songs', 'album_id': album.album_id, 'item_type': 'album'})
        cmd = 'Container.Update({album_url})'.format(album_url=album_url)
        commands = [('Go to album', cmd)]
        li.addContextMenuItems(commands)
        items.append((url, li, False))
    return items


def get_band_items(bands):
    items = []
    for band in bands:
        li = xbmcgui.ListItem(label=band.band_name)
        url = _build_url({'mode': 'list_albums', 'band_id': band.band_id})
        items.append((url, li, True))
    return items
