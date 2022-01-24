import sys
import os
from urllib.parse import urlencode, parse_qsl
import xbmcgui, xbmcplugin, xbmcaddon, xbmcvfs
import requests
from resources.functions import *

# Get the plugin url in plugin:// notation.
_url = sys.argv[0]
# Get the plugin handle as an integer number.
_handle = int(sys.argv[1])
#addonPath = xbmcvfs.translatePath(xbmcaddon.Addon(id='plugin.video.ufanettv').getAddonInfo('path'))
# Check that login and password available
checkSettings(_handle)
# Get deviceID
deviceID = checkDeviceID(_handle)

# Get token
getToken = requests.post('http://api.ufanet.platform24.tv/v2/auth/device', json={"device_id": deviceID})
for el in getToken.json():
    if el == 'access_token':
        accessToken = getToken.json().get('access_token')
    if el == 'error_code':
        file = open(profilePath + 'DeviceID.txt', 'w')
        file.write('')
        file.close()
        deviceID = checkDeviceID(_handle)

# Get Archive IDs
paramsArch = {'version': '2.5', "access_token": accessToken}
getArchive = requests.get('http://api.ufanet.platform24.tv/v2/programs/filters', params=paramsArch)
ARCHIVE = {}
for el in getArchive.json():
    ARCHIVE[str(el['id'])] = el['filters']


def get_url(**kwargs):
    return '{0}?{1}'.format(_url, urlencode(kwargs))

def get_classes():
    CLASSES = {}
    CLASSES['ТВ каналы'] = 'tvchannels'
    paramsClasse = {'version': '2.5', "access_token": accessToken}
    getClasses = requests.get('http://api.ufanet.platform24.tv/v2/programs/filters', params=paramsClasse)
    for el in getClasses.json():
        CLASSES[el['name']] = str(el['id'])
#    CLASSES['Профиль'] = 'profile'
    return CLASSES

def get_categories():
    paramsChan = {"includes": "images.whiteback", "access_token": accessToken}
    getChannels = requests.get('http://api.ufanet.platform24.tv/v2/channels/categories', params=paramsChan)
    TVCHANNELS = {}
    for cat in getChannels.json():
        TVCHANNELS[cat['name']] = channelFunc(cat['channels'])
    return TVCHANNELS

def get_videos(category):
    someList = []
    someDict = {}
    for el in category[2:-1].replace('},', '').replace('}', '').split('{'):
        elList = []
        for ele in el.replace('\'', '').strip().split(', '):
            elList.append(ele.split(': '))
        someList.append(dict(elList))
    return someList

def get_films(id):
    paramsFilms = {'access_token': accessToken, 'limit': '100', 'offset': '0', 'filters': id, 'search': ''}
    getFilms = requests.get('http://api.ufanet.platform24.tv/v2/programs', params=paramsFilms)
    FILMS = {}
    for film in getFilms.json():
        FILMS[film['title']] = filmFunc(film)
    return FILMS

def get_filmsCats(id):
    return ARCHIVE[id]

def get_views(film):
    paramsView = {'access_token': accessToken}
    getView = requests.get('http://api.ufanet.platform24.tv/v2/programs/' + film + '/schedule', params=paramsView)
    return getView.json()


def list_classes():
    xbmcplugin.setPluginCategory(_handle, 'classes')
    xbmcplugin.setContent(_handle, 'videos')
    classes = get_classes()
    for classe in classes:
        list_item = xbmcgui.ListItem(label=classe)
        if classes[classe] == 'tvchannels': url = get_url(action='listTvChannels', classe=classe)
        elif classes[classe] == 'profile':
            is_folder = False
            url = get_url(action='listProfile', classe=classe)
            xbmcplugin.addDirectoryItem(_handle, url, list_item, is_folder)
            continue
        else: url = get_url(action='listCategories', classe=classes[classe])
        is_folder = True
        xbmcplugin.addDirectoryItem(_handle, url, list_item, is_folder)
#    listitem = xbmcgui.ListItem(label='Профиль')
#    listitem.setProperty('SpecialSort', 'bottom')
#    xbmcplugin.addDirectoryItem(_handle, url, listitem, is_folder)
    xbmcplugin.endOfDirectory(_handle)


def listFilmsCats(id):
    xbmcplugin.setPluginCategory(_handle, 'Films')
    xbmcplugin.setContent(_handle, 'videos')
    films = get_filmsCats(id)
    for film in films:
        list_item = xbmcgui.ListItem(label=film['name'])
        list_item.setInfo('video', {'title': film['name'], 'mediatype': 'video'})
        url = get_url(action='listFilmsCats', film=film['id'])
        # is_folder = True means that this item opens a sub-list of lower level items.
        is_folder = True
        # Add our item to the Kodi virtual folder listing.
        xbmcplugin.addDirectoryItem(_handle, url, list_item, is_folder)
    # Add a sort method for the virtual folder items (alphabetically, ignore articles)
    xbmcplugin.addSortMethod(_handle, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)
    # Finish creating a virtual folder.
    xbmcplugin.endOfDirectory(_handle)


def listFilms(id):
    xbmcplugin.setPluginCategory(_handle, 'Films')
    xbmcplugin.setContent(_handle, 'videos')
    films = get_films(id)
    for film in films:
        list_item = xbmcgui.ListItem(label=films[film][0]['name'])
        list_item.setArt({'thumb': films[film][0]['thumb'], 'icon': films[film][0]['thumb'], 'fanart': films[film][0]['thumb']})
        list_item.setInfo('video', {'title': film, 'genre': film, 'mediatype': 'video'})
        url = get_url(action='views', film=films[film][0]['id'])
        # is_folder = True means that this item opens a sub-list of lower level items.
        is_folder = True
        # Add our item to the Kodi virtual folder listing.
        xbmcplugin.addDirectoryItem(_handle, url, list_item, is_folder)
    # Add a sort method for the virtual folder items (alphabetically, ignore articles)
    xbmcplugin.addSortMethod(_handle, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)
    # Finish creating a virtual folder.
    xbmcplugin.endOfDirectory(_handle)


def listTvChannels():
    xbmcplugin.setPluginCategory(_handle, 'Categories')
    xbmcplugin.setContent(_handle, 'videos')
    categories = get_categories()
    for category in categories:
        list_item = xbmcgui.ListItem(label=category)
        list_item.setArt({'thumb': categories[category][0]['thumb'],
                          'icon': categories[category][0]['thumb'],
                          'fanart': categories[category][0]['thumb']})
        list_item.setInfo('video', {'title': categories[category][0]['name'],
                                    'genre': categories[category][0]['name'],
                                    'mediatype': 'video'})
        url = get_url(action='listing', category=categories[category])
        is_folder = True
        xbmcplugin.addDirectoryItem(_handle, url, list_item, is_folder)
    xbmcplugin.endOfDirectory(_handle)


def listViews(film):
    xbmcplugin.setPluginCategory(_handle, film)
    xbmcplugin.setContent(_handle, 'videos')
    videos = get_views(film)
    for video in videos:
        list_item = xbmcgui.ListItem(label=video['channel']['name'])
        if video['episode'] is None:
            episode = ""
        else:
            episode = 'S' + str(video['episode']['season']) + 'E' + str(video['episode']['series']) + ' ' + str(video['episode']['title'])
        list_item.setInfo('video', {'title': video['channel']['name'] + " " + episode + " " + video['date'] + ' ' + video['time'],
                                    'genre': str(video['program']['category']['name']),
                                    'mediatype': 'video'})
        list_item.setArt({'thumb': video['channel']['icon'], 'icon': video['channel']['icon'], 'fanart': video['channel']['icon']})
        # Set 'IsPlayable' property to 'true'.
        # This is mandatory for playable items!
        list_item.setProperty('IsPlayable', 'true')
        # Create a URL for a plugin recursive call.
        # Example: plugin://plugin.video.example/?action=play&video=http://www.vidsplay.com/wp-content/uploads/2017/04/crab.mp4
        url = get_url(action='playView', video=str(video['channel_id']) + " " + str(video['timestamp']))
        # Add the list item to a virtual Kodi folder.
        # is_folder = False means that this item won't open any sub-list.
        is_folder = False
        # Add our item to the Kodi virtual folder listing.
        xbmcplugin.addDirectoryItem(_handle, url, list_item, is_folder)
    # Add a sort method for the virtual folder items (alphabetically, ignore articles)
    xbmcplugin.addSortMethod(_handle, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)
#    listitem = xbmcgui.ListItem(label='Next page')
#    listitem.setProperty('SpecialSort', 'bottom')
#    xbmcplugin.addDirectoryItem(_handle, url, listitem, is_folder)
    # Finish creating a virtual folder.
    xbmcplugin.endOfDirectory(_handle)


def listTvVideos(category):
    xbmcplugin.setPluginCategory(_handle, 'Каналы')
    xbmcplugin.setContent(_handle, 'videos')
    videos = get_videos(category)
    for video in videos:
        list_item = xbmcgui.ListItem(label=video['name'])
        list_item.setInfo('video', {'title': video['name'], 'genre': video['genre'], 'mediatype': 'video'})
        list_item.setArt({'thumb': video['thumb'], 'icon': video['thumb'], 'fanart': video['thumb']})
        list_item.setProperty('IsPlayable', 'true')
        url = get_url(action='play', video=video['video'])
        is_folder = False
        xbmcplugin.addDirectoryItem(_handle, url, list_item, is_folder)
    xbmcplugin.addSortMethod(_handle, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)
#    listitem = xbmcgui.ListItem(label='Next page')
#    listitem.setProperty('SpecialSort', 'bottom')
#    xbmcplugin.addDirectoryItem(_handle, url, listitem, is_folder)
    # Finish creating a virtual folder.
    xbmcplugin.endOfDirectory(_handle)


def showProfile():
    pass


def play_view(path):
    paramsChan = {"access_token": accessToken, "ts": path.split()[1]}
    urlJson = requests.get('http://api.ufanet.platform24.tv/v2/channels/' + path.split()[0] + '/stream', params=paramsChan)
    try:
        if urlJson.json()['error']:
            xbmcgui.Dialog().ok('Внимание!', str(urlJson.json()['error']['message']))
            return
    except:
        url = urlJson.json()['hls']
    # Create a playable item with a path to play.
    play_item = xbmcgui.ListItem(path=url)
    # Pass the item to the Kodi player.
    xbmcplugin.setResolvedUrl(_handle, True, listitem=play_item)


def play_video(path):
    paramsChan = {"access_token": accessToken, "ts": "0"}
    urlJson = requests.get('http://api.ufanet.platform24.tv/v2/channels/' + path + '/stream', params=paramsChan)
    try:
        if urlJson.json()['error']:
            xbmcgui.Dialog().ok('Внимание!', str(urlJson.json()['error']['message']))
            return
    except:
        url = urlJson.json()['hls']
    # Create a playable item with a path to play.
    play_item = xbmcgui.ListItem(path=url)
    # Pass the item to the Kodi player.
    xbmcplugin.setResolvedUrl(_handle, True, listitem=play_item)


def router(paramstring):
    # Parse a URL-encoded paramstring to the dictionary of
    # {<parameter>: <value>} elements
    params = dict(parse_qsl(paramstring))
    if params:
        if params['action'] == 'listing':
            listTvVideos(params['category'])
        elif params['action'] == 'play':
            play_video(params['video'])
        elif params['action'] == 'listTvChannels':
            listTvChannels()
        elif params['action'] == 'listCategories':
            listFilmsCats(params['classe'])
        elif params['action'] == 'listFilmsCats':
            listFilms(params['film'])
        elif params['action'] == 'listProfile':
            showProfile()
        elif params['action'] == 'views':
            listViews(params['film'])
        elif params['action'] == 'playView':
            play_view(params['video'])
        else:
            raise ValueError('Invalid paramstring: {0}!'.format(paramstring))
    else:
        list_classes()


if __name__ == '__main__':
    router(sys.argv[2][1:])
