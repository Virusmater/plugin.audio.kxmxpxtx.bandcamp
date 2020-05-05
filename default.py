# https://docs.python.org/2.7/
import sys
import urllib
from future.standard_library import install_aliases
install_aliases()
from future.utils import (PY3)
if PY3:
    from urllib.parse import parse_qs
else:
    from urlparse import parse_qs

from urllib.parse import urlencode
import xbmcgui
import xbmcplugin
import xbmcaddon
import xbmc
from resources.lib.bandcamp_api import bandcamp
from resources.lib.bandcamp_api.bandcamp import Band


def build_url(query):
    base_url = sys.argv[0]
    return base_url + '?' + urlencode(query)

def build_main_menu():
    is_folder = True
    #discover menu
    list_item = xbmcgui.ListItem(label='discover')
    url = build_url({'mode': 'list_discover'})
    xbmcplugin.addDirectoryItem(addon_handle, url, list_item, is_folder)
    #collection menu
    #don't add if not configured
    if username == "":
        list_item = xbmcgui.ListItem(label='add username to access collection')
        url = build_url({'mode': 'settings'})
        xbmcplugin.addDirectoryItem(addon_handle, url, list_item, is_folder)
    else:
        list_item = xbmcgui.ListItem(label='collection')
        url = build_url({'mode': 'list_collection'})
        xbmcplugin.addDirectoryItem(addon_handle, url, list_item, is_folder)
    xbmcplugin.endOfDirectory(addon_handle)


def build_band_list(bands):
    band_list = []
    for band in bands:
        li = xbmcgui.ListItem(label=band.band_name)
        url = build_url({'mode': 'list_albums', 'band_id': band.band_id})
        band_list.append((url, li, True))
    xbmcplugin.addDirectoryItems(addon_handle, band_list, len(band_list))
    xbmcplugin.addSortMethod(addon_handle, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)
    xbmcplugin.endOfDirectory(addon_handle)


def build_album_list(albums):
    albums_list = []
    for album in albums:
        li = xbmcgui.ListItem(label=album.album_name)
        url = build_url({'mode': 'list_songs', 'album_id': album.album_id})
        li.setArt({'thumb': album.get_art_img(), 'fanart': album.get_art_img()})
        albums_list.append((url, li, True))
    xbmcplugin.addDirectoryItems(addon_handle, albums_list, len(albums_list))
    xbmcplugin.endOfDirectory(addon_handle)

def build_genre_list():
    # all
    list_item = xbmcgui.ListItem(label='all')
    url = build_url({'mode': 'list_subgenre_songs', 'category': 'all', 'subcategory': 'all'})
    is_folder = True
    xbmcplugin.addDirectoryItem(addon_handle, url, list_item, is_folder)
    genres = bandcamp.get_genres()
    for genre in genres:
        list_item = xbmcgui.ListItem(label=genre['name'])
        url = build_url({'mode': 'list_subgenre', 'category': genre['value']})
        is_folder = True
        xbmcplugin.addDirectoryItem(addon_handle, url, list_item, is_folder)
    xbmcplugin.endOfDirectory(addon_handle)


def build_subgenre_list(genre):
    list_item = xbmcgui.ListItem(label='all '+genre)
    url = build_url({'mode': 'list_subgenre_songs', 'category': genre, 'subcategory': 'all'})
    is_folder = True
    xbmcplugin.addDirectoryItem(addon_handle, url, list_item, is_folder)
    genres = bandcamp.get_subgenres()
    for subgenre in genres[genre]:
        list_item = xbmcgui.ListItem(label=subgenre['name'])
        url = build_url({'mode': 'list_subgenre_songs', 'category': genre, 'subcategory': subgenre['value']})
        is_folder = True
        xbmcplugin.addDirectoryItem(addon_handle, url, list_item, is_folder)
    xbmcplugin.endOfDirectory(addon_handle)


def build_song_list(album, tracks):
    song_list = []
    for track in tracks:
        title = u"{number}. {track}".format(number=track.number, track=track.track_name)
        li = xbmcgui.ListItem(label=title)
        li.setInfo('music', {'duration': int(track.duration), 'tracknumber': track.number})
        li.setArt({'thumb': album.get_art_img(), 'fanart': album.get_art_img()})
        li.setProperty('IsPlayable', 'true')
        url = build_url({'mode': 'stream', 'url': track.file, 'title': title})
        song_list.append((url, li, False))
    xbmcplugin.addDirectoryItems(addon_handle, song_list, len(song_list))
    xbmcplugin.setContent(addon_handle, 'songs')
    xbmcplugin.endOfDirectory(addon_handle)

def build_featured_list(bands):
    song_list = []
    for band in bands:
        for album in bands[band]:
            for track in bands[band][album]:
                title = u"{band} - {track}".format(band=band.band_name, track=track.track_name)
                li = xbmcgui.ListItem(label=title)
                li.setInfo('music', {'duration': int(track.duration)})
                li.setArt({'thumb': album.get_art_img(), 'fanart':album.get_art_img()})
                li.setProperty('IsPlayable', 'true')
                url = build_url({'mode': 'stream', 'url': track.file, 'title': title})
                song_list.append((url, li, False))
    xbmcplugin.addDirectoryItems(addon_handle, song_list, len(song_list))
    xbmcplugin.setContent(addon_handle, 'songs')
    xbmcplugin.endOfDirectory(addon_handle)


def play_song(url):
    play_item = xbmcgui.ListItem(path=url)
    xbmcplugin.setResolvedUrl(addon_handle, True, listitem=play_item)


def main():
    args = parse_qs(sys.argv[2][1:])
    mode = args.get('mode', None)
    if mode is None:
        build_main_menu()
    elif mode[0] == 'stream':
        play_song(args['url'][0])
    elif mode[0] == 'list_discover':
        build_genre_list()
    elif mode[0] == 'list_collection':
        build_band_list(bandcamp.get_collection(bandcamp.get_fan_id()))
    elif mode[0] == 'list_albums':
        bands = bandcamp.get_collection(bandcamp.get_fan_id())
        band = Band(band_id=args.get('band_id', None)[0])
        build_album_list(bands[band])
    elif mode[0] == 'list_songs':
        album_id = args.get('album_id', None)[0]
        build_song_list(*bandcamp.get_album(album_id))
    elif mode[0] == 'list_subgenre':
        genre = args.get('category', None)[0]
        build_subgenre_list(genre)
    elif mode[0] == 'list_subgenre_songs':
        genre = args.get('category', None)[0]
        subgenre = args.get('subcategory', None)[0]
        build_featured_list(bandcamp.discover(genre, subgenre))
    elif mode[0] == 'settings':
        my_addon.openSettings()


if __name__ == '__main__':
    my_addon = xbmcaddon.Addon()
    username = my_addon.getSetting('username')  # returns the string 'true' or 'false'
    bandcamp = bandcamp.Bandcamp(username)
    addon_handle = int(sys.argv[1])
    main()
