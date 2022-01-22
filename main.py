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

# Get channels
paramsChan = {"includes": "images.whiteback", "access_token": accessToken}
getChannels = requests.get('http://api.ufanet.platform24.tv/v2/channels/categories', params=paramsChan)

TVCHANNELS = {}
for cat in getChannels.json():
    TVCHANNELS[cat['name']] = channelFunc(cat['channels'])


CLASSES = {}
CLASSES['ТВ каналы'] = [TVCHANNELS]
CLASSES['Фильмы'] = ['films']
CLASSES['Сериалы'] = ['serials']
CLASSES['Детям'] = ['children']
CLASSES['Передачи'] = ['programms']
CLASSES['Спорт'] = ['sport']

def get_url(**kwargs):
    return '{0}?{1}'.format(_url, urlencode(kwargs))

def get_classes():
    return CLASSES.keys()

def get_categories():
    return TVCHANNELS.keys()

def get_videos(category):
    return TVCHANNELS[category]

def get_films(id):
    paramsFilms = {'access_token': accessToken, 'limit': '100', 'offset': '0', 'filters': id, 'search': ''}
    getFilms = requests.get('http://api.ufanet.platform24.tv/v2/programs', params=paramsFilms)
    FILMS = {}
    for film in getFilms.json():
        FILMS[film['title']] = filmFunc(film)
    return FILMS

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
        if classe == 'ТВ каналы': url = get_url(action='listTvChannels', classe=classe)
        elif classe == 'Фильмы': url = get_url(action='listFilms', classe=classe)
        elif classe == 'Сериалы': url = get_url(action='listSerials', classe=classe)
        elif classe == 'Детям': url = get_url(action='listDetyam', classe=classe)
        elif classe == 'Передачи': url = get_url(action='listPrograms', classe=classe)
        elif classe == 'Спорт': url = get_url(action='listSport', classe=classe)
        else: url = get_url(action='listTvChannels', classe=classe)
        is_folder = True
        xbmcplugin.addDirectoryItem(_handle, url, list_item, is_folder)
    listitem = xbmcgui.ListItem(label='Профиль')
    listitem.setProperty('SpecialSort', 'bottom')
    xbmcplugin.addDirectoryItem(_handle, url, listitem, is_folder)
    xbmcplugin.endOfDirectory(_handle)


def listFilms(id):
    xbmcplugin.setPluginCategory(_handle, 'Films')
    xbmcplugin.setContent(_handle, 'videos')
    # Get video categories
    films = get_films(id)
    # Iterate through categories
    for film in films:
        list_item = xbmcgui.ListItem(label=films[film][0]['name'])
        # Set graphics (thumbnail, fanart, banner, poster, landscape etc.) for the list item.
        # Here we use the same image for all items for simplicity's sake.
        # In a real-life plugin you need to set each image accordingly.
        #list_item.setArt({'thumb': FILMS[film][0]['thumb'],
        #                  'icon': FILMS[film][0]['thumb'],
        #                  'fanart': FILMS[film][0]['thumb']})
        list_item.setArt({'thumb': films[film][0]['thumb'],
                          'icon': films[film][0]['thumb'],
                          'fanart': films[film][0]['thumb']})
        # Set additional info for the list item.
        # Here we use a category name for both properties for for simplicity's sake.
        # setInfo allows to set various information for an item.
        # For available properties see the following link:
        # https://codedocs.xyz/xbmc/xbmc/group__python__xbmcgui__listitem.html#ga0b71166869bda87ad744942888fb5f14
        # 'mediatype' is needed for a skin to display info for this ListItem correctly.
        list_item.setInfo('video', {'title': film,
                                    'genre': film,
                                    'mediatype': 'video'})
        # Create a URL for a plugin recursive call.
        # Example: plugin://plugin.video.example/?action=listing&category=Animals
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
    # Get video categories
    categories = get_categories()
    # Iterate through categories
    for category in categories:
        list_item = xbmcgui.ListItem(label=category)
        # Set graphics (thumbnail, fanart, banner, poster, landscape etc.) for the list item.
        # Here we use the same image for all items for simplicity's sake.
        # In a real-life plugin you need to set each image accordingly.
        list_item.setArt({'thumb': TVCHANNELS[category][0]['thumb'],
                          'icon': TVCHANNELS[category][0]['thumb'],
                          'fanart': TVCHANNELS[category][0]['thumb']})
        # Set additional info for the list item.
        # Here we use a category name for both properties for for simplicity's sake.
        # setInfo allows to set various information for an item.
        # For available properties see the following link:
        # https://codedocs.xyz/xbmc/xbmc/group__python__xbmcgui__listitem.html#ga0b71166869bda87ad744942888fb5f14
        # 'mediatype' is needed for a skin to display info for this ListItem correctly.
        list_item.setInfo('video', {'title': category,
                                    'genre': category,
                                    'mediatype': 'video'})
        # Create a URL for a plugin recursive call.
        # Example: plugin://plugin.video.example/?action=listing&category=Animals
        url = get_url(action='listing', category=category)
        # is_folder = True means that this item opens a sub-list of lower level items.
        is_folder = True
        # Add our item to the Kodi virtual folder listing.
        xbmcplugin.addDirectoryItem(_handle, url, list_item, is_folder)
    # Add a sort method for the virtual folder items (alphabetically, ignore articles)
#    xbmcplugin.addSortMethod(_handle, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)
    # Finish creating a virtual folder.
    xbmcplugin.endOfDirectory(_handle)


def listViews(film):
    # Set plugin category. It is displayed in some skins as the name
    # of the current section.
    xbmcplugin.setPluginCategory(_handle, film)
    # Set plugin content. It allows Kodi to select appropriate views
    # for this type of content.
    xbmcplugin.setContent(_handle, 'videos')
    # Get the list of videos in the category.
    videos = get_views(film)
    # Iterate through videos.
    for video in videos:
        # Create a list item with a text label and a thumbnail image.
        list_item = xbmcgui.ListItem(label=video['channel']['name'])
        # Set additional info for the list item.
        # 'mediatype' is needed for skin to display info for this ListItem correctly.
        if video['episode'] is None:
            episode = ""
        else:
            episode = 'S' + str(video['episode']['season']) + 'E' + str(video['episode']['series']) + ' ' + str(video['episode']['title'])
        list_item.setInfo('video', {'title': video['channel']['name'] + " " + episode + " " + video['date'] + ' ' + video['time'],
                                    'genre': str(video['program']['category']['name']),
                                    'mediatype': 'video'})
        # Set graphics (thumbnail, fanart, banner, poster, landscape etc.) for the list item.
        # Here we use the same image for all items for simplicity's sake.
        # In a real-life plugin you need to set each image accordingly.
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
    # Set plugin category. It is displayed in some skins as the name
    # of the current section.
    xbmcplugin.setPluginCategory(_handle, category)
    # Set plugin content. It allows Kodi to select appropriate views
    # for this type of content.
    xbmcplugin.setContent(_handle, 'videos')
    # Get the list of videos in the category.
    videos = get_videos(category)
    # Iterate through videos.
    for video in videos:
        # Create a list item with a text label and a thumbnail image.
        list_item = xbmcgui.ListItem(label=video['name'])
        # Set additional info for the list item.
        # 'mediatype' is needed for skin to display info for this ListItem correctly.
        list_item.setInfo('video', {'title': video['name'],
                                    'genre': video['genre'],
                                    'mediatype': 'video'})
        # Set graphics (thumbnail, fanart, banner, poster, landscape etc.) for the list item.
        # Here we use the same image for all items for simplicity's sake.
        # In a real-life plugin you need to set each image accordingly.
        list_item.setArt({'thumb': video['thumb'], 'icon': video['thumb'], 'fanart': video['thumb']})
        # Set 'IsPlayable' property to 'true'.
        # This is mandatory for playable items!
        list_item.setProperty('IsPlayable', 'true')
        # Create a URL for a plugin recursive call.
        # Example: plugin://plugin.video.example/?action=play&video=http://www.vidsplay.com/wp-content/uploads/2017/04/crab.mp4
        url = get_url(action='play', video=video['video'])
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
    """
    Router function that calls other functions
    depending on the provided paramstring

    :param paramstring: URL encoded plugin paramstring
    :type paramstring: str
    """
    # Parse a URL-encoded paramstring to the dictionary of
    # {<parameter>: <value>} elements
    params = dict(parse_qsl(paramstring))
    # Check the parameters passed to the plugin
    if params:
        if params['action'] == 'listing':
            # Display the list of videos in a provided category.
            listTvVideos(params['category'])
        elif params['action'] == 'play':
            # Play a video from a provided URL.
            play_video(params['video'])
        elif params['action'] == 'listTvChannels':
            listTvChannels()
        elif params['action'] == 'listFilms':
            listFilms(5000)
        elif params['action'] == 'listSerials':
            listFilms(6000)
        elif params['action'] == 'listDetyam':
            listFilms(7000)
        elif params['action'] == 'listPrograms':
            listFilms(8000)
        elif params['action'] == 'listSport':
            listFilms(9000)
        elif params['action'] == 'views':
            listViews(params['film'])
        elif params['action'] == 'playView':
            play_view(params['video'])
        else:
            # If the provided paramstring does not contain a supported action
            # we raise an exception. This helps to catch coding errors,
            # e.g. typos in action names.
            raise ValueError('Invalid paramstring: {0}!'.format(paramstring))
    else:
        list_classes()

if __name__ == '__main__':
    # Call the router function and pass the plugin call parameters to it.
    # We use string slicing to trim the leading '?' from the plugin call paramstring
    router(sys.argv[2][1:])
