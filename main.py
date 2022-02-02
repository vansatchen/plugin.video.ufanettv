import sys
from urllib.parse import urlencode, parse_qsl
import xbmcgui, xbmcplugin, xbmcaddon, xbmcvfs
import requests
from resources.functions import *

# Get the plugin url in plugin:// notation.
_url = sys.argv[0]
# Get the plugin handle as an integer number.
_handle = int(sys.argv[1])
addonPath = xbmcvfs.translatePath(xbmcaddon.Addon(id='plugin.video.ufanettv').getAddonInfo('path'))
defaultImage = addonPath + 'resources/tv.png'
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

paramsArch = {'version': '2.5', "access_token": accessToken}
getArchive = requests.get('http://api.ufanet.platform24.tv/v2/programs/filters', params=paramsArch)
getSubscriptions = requests.get('http://api.ufanet.platform24.tv/v2/videos/filters', params=paramsArch)


def get_url(**kwargs):
    return '{0}?{1}'.format(_url, urlencode(kwargs))

def getClasses():
    CLASSES = {}
#    CLASSES['Поиск'] = 'search'
    CLASSES['ТВ каналы'] = 'tvchannels'
    for el in getArchive.json():
        CLASSES[el['name']] = str(el['id'])
    return CLASSES

def getArchCats(id):
    ARCHIVE = {}
    for el in getArchive.json():
        ARCHIVE[str(el['id'])] = el['filters']
    return ARCHIVE[id]

def getSubs():
    SUBSCRIPTIONS = {}
    for el in getSubscriptions.json():
        SUBSCRIPTIONS[el['name']] = str(el['id'])
    return SUBSCRIPTIONS

def getSubsCats(id):
    SUBS = {}
    for el in getSubscriptions.json():
        SUBS[str(el['id'])] = el['filters']
    return SUBS[id]

def getTvCategories():
    paramsChan = {"includes": "images.whiteback", "access_token": accessToken}
    getChannels = requests.get('http://api.ufanet.platform24.tv/v2/channels/categories', params=paramsChan)
    TVCHANNELS = {}
    for cat in getChannels.json():
        TVCHANNELS[cat['name']] = channelFunc(cat['channels'])
    return TVCHANNELS

def getArchFilms(id):
    paramsFilms = {'access_token': accessToken, 'limit': '100', 'offset': '0', 'filters': id, 'search': ''}
    getFilms = requests.get('http://api.ufanet.platform24.tv/v2/programs', params=paramsFilms)
    FILMS = {}
    for film in getFilms.json():
        FILMS[film['title']] = filmFunc(film)
    return FILMS

def getSubsFilms(id):
    paramsSubs = {'access_token': accessToken, 'limit': '100', 'offset': '0', 'filters': id, 'search': ''}
    getSubs = requests.get('http://api.ufanet.platform24.tv/v2/videos', params=paramsSubs)
    SUBS = {}
    for sub in getSubs.json():
        SUBS[sub['title']] = filmFunc(sub)
    return SUBS

def get_videos(category):
    someList = []
    for el in category[2:-1].replace('},', '').replace('}', '').split('{'):
        elList = []
        for ele in el.replace('\'', '').strip().split(', '):
            elList.append(ele.split(': '))
        someList.append(dict(elList))
    return someList

def getArchViews(film):
    paramsView = {'access_token': accessToken}
    getView = requests.get('http://api.ufanet.platform24.tv/v2/programs/' + film + '/schedule', params=paramsView)
    return getView.json()


# Total
def list_classes():
    xbmcplugin.setPluginCategory(_handle, '')
    xbmcplugin.setContent(_handle, 'videos')
    defaultFanart = addonPath + 'resources/icons/tv.jpg'
    # List TVchannels and archive
    classes = getClasses()
    for classe in classes:
        list_item = xbmcgui.ListItem(label=classe)
        if classes[classe] == 'tvchannels': url = get_url(action='listTvChannels', classe=classe)
        elif classes[classe] == 'profile':
            is_folder = False
            url = get_url(action='listProfile', classe=classe)
            xbmcplugin.addDirectoryItem(_handle, url, list_item, is_folder)
            continue
        else: url = get_url(action='listArchCategories', classe=classes[classe])
        if classe == 'ТВ каналы': list_item.setArt({'thumb': addonPath + 'resources/icons/tv.jpg', 'fanart': defaultFanart})
        elif classe == 'Фильмы': list_item.setArt({'thumb': addonPath + 'resources/icons/serials.png', 'fanart': defaultFanart})
        elif classe == 'Сериалы': list_item.setArt({'thumb': addonPath + 'resources/icons/films.png', 'fanart': defaultFanart})
        elif classe == 'Детям': list_item.setArt({'thumb': addonPath + 'resources/icons/children.png', 'fanart': defaultFanart})
        elif classe == 'Передачи': list_item.setArt({'thumb': addonPath + 'resources/icons/programs.png', 'fanart': defaultFanart})
        elif classe == 'Спорт': list_item.setArt({'thumb': addonPath + 'resources/icons/sport.png', 'fanart': defaultFanart})
        elif classe == 'Поиск':
            list_item.setArt({'thumb': addonPath + 'resources/icons/search.png', 'fanart': defaultFanart})
            url = get_url(action='search', classe='search')
        else: list_item.setArt({'thumb': addonPath + 'resources/icons/tv1.png', 'fanart': defaultFanart})
        is_folder = True
        xbmcplugin.addDirectoryItem(_handle, url, list_item, is_folder)
    # List subscriptions
    subs = getSubs()
    for sub in subs:
        list_item = xbmcgui.ListItem(label=sub)
        url = get_url(action='listSubscriptions', sub=subs[sub])
        if sub == 'UTV Лучшее': list_item.setArt({'thumb': addonPath + 'resources/icons/utv.png', 'fanart': defaultFanart})
        elif sub == 'AMEDIATEKA': list_item.setArt({'thumb': addonPath + 'resources/icons/amediateka.png', 'fanart': defaultFanart})
        elif sub == 'MEGOGO': list_item.setArt({'thumb': addonPath + 'resources/icons/megogo.jpg', 'fanart': defaultFanart})
        elif sub == 'START': list_item.setArt({'thumb': addonPath + 'resources/icons/start.jpg', 'fanart': defaultFanart})
        elif sub == 'Живи активно': list_item.setArt({'thumb': addonPath + 'resources/icons/zhiviaktivno.png', 'fanart': defaultFanart})
        elif sub == 'Шао Сан': list_item.setArt({'thumb': addonPath + 'resources/icons/shaosan.png', 'fanart': defaultFanart})
        elif sub == 'Dizi': list_item.setArt({'thumb': addonPath + 'resources/icons/dizi.jpg', 'fanart': defaultFanart})
        else: list_item.setArt({'thumb': addonPath + 'resources/icons/tv1.png', 'fanart': defaultFanart})
        is_folder = True
        xbmcplugin.addDirectoryItem(_handle, url, list_item, is_folder)
#    listitem = xbmcgui.ListItem(label='Профиль')
#    listitem.setProperty('SpecialSort', 'bottom')
#    listitem.setProperty('IsPlayable', 'false')
#    listitem.setArt({'thumb': addonPath + 'resources/icons/profile.png'})
#    url = get_url(action='listProfile', act='some')
#    is_folder = False
#    xbmcplugin.addDirectoryItem(_handle, url, listitem, is_folder)
    xbmcplugin.endOfDirectory(_handle)


# Total
def listCats(id, param):
    if param == 'tv':
        catTitle = 'Категории'
        elements = getTvCategories()
        action = 'listTvCats'
    elif param == 'arch':
        catTitle = 'Жанры'
        elements = getArchCats(id)
        action = 'listArchFilmsCats'
        xbmcplugin.addSortMethod(_handle, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)
    elif param == 'sub':
        catTitle = 'Содержимое'
        elements = getSubsCats(id)
        action = 'listSubsCats'
        xbmcplugin.addSortMethod(_handle, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)
    xbmcplugin.setContent(_handle, 'videos')
    for element in elements:
        if param == 'tv':
            label = element
            thumb = elements[element][0]['thumb']
            name = elements[element][0]['name']
            elem = elements[element]
        else:
            label = element['name']
            thumb = thumbForGenre(label)
            name = element['name']
            elem = element['id']
        list_item = xbmcgui.ListItem(label=label)
        list_item.setArt({'thumb': thumb, 'icon': thumb, 'fanart': thumb})
        list_item.setInfo('video', {'title': name, 'genre': name, 'mediatype': 'video'})
        url = get_url(action=action, el=elem)
        is_folder = True
        xbmcplugin.addDirectoryItem(_handle, url, list_item, is_folder)
    xbmcplugin.endOfDirectory(_handle)


def listArchFilms(id):
    xbmcplugin.setPluginCategory(_handle, 'Films')
    xbmcplugin.setContent(_handle, 'videos')
    films = getArchFilms(id)
    for film in films:
        list_item = xbmcgui.ListItem(label=films[film][0]['name'])
        list_item.setArt({'thumb': films[film][0]['thumb'], 'icon': films[film][0]['thumb'], 'fanart': films[film][0]['thumb']})
        list_item.setInfo('video', {'title': film, 'genre': films[film][0]['genre'], 'mediatype': 'video'})
        url = get_url(action='archViews', film=films[film][0]['id'])
        is_folder = True
        xbmcplugin.addDirectoryItem(_handle, url, list_item, is_folder)
    xbmcplugin.addSortMethod(_handle, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)
    xbmcplugin.endOfDirectory(_handle)


# Total
def listVideos(id, param):
    if param == 'sub':
        listTitle = 'Выпуски'
        elements = getSubsFilms(id)
    elif param == 'arch':
        listTitle = 'Архив'
        elements = getArchViews(id)
    elif param == 'tv':
        listTitle = 'ТВ-каналы'
        elements = get_videos(id)
    xbmcplugin.setPluginCategory(_handle, listTitle)
    xbmcplugin.setContent(_handle, 'videos')
    for element in elements:
        if param == 'sub':
            list_item = xbmcgui.ListItem(label=elements[element][0]['name'])
            list_item.setInfo('video', {'title': element, 'genre': elements[element][0]['genre'], 'mediatype': 'video'})
            thumb = elements[element][0]['thumb']
            el = elements[element][0]['id']
            action = 'playSubs'
        elif param == 'arch':
            list_item = xbmcgui.ListItem(label=element['channel']['name'])
            if element['episode'] is None:
                episode = ""
            else:
                infoStr = element['episode']
                episode = 'S' + str(infoStr['season']) + 'E' + str(infoStr['series']) + ' ' + str(infoStr['title'])
            list_item.setInfo('video', {'title': element['channel']['name'] + " " + episode + " " + element['date'] + ' ' + element['time'],
                                        'genre': str(element['program']['category']['name']), 'mediatype': 'video'})
            thumb = element['channel']['icon']
            action = 'playArch'
            el = str(element['channel_id']) + " " + str(element['timestamp'])
        elif param == 'tv':
            list_item = xbmcgui.ListItem(label=element['name'])
            list_item.setInfo('video', {'title': element['name'], 'genre': element['genre'], 'mediatype': 'video'})
            thumb = element['thumb']
            el = element['video']
            action = 'playTv'
        list_item.setArt({'thumb': thumb, 'icon': thumb, 'fanart': thumb})
        list_item.setProperty('IsPlayable', 'true')
        url = get_url(action=action, el=el)
        is_folder = False
        xbmcplugin.addDirectoryItem(_handle, url, list_item, is_folder)
    xbmcplugin.endOfDirectory(_handle)


# Total
def play_video(id, param):
    if param == 'arch':
        paramsVideo = {"access_token": accessToken, "ts": id.split()[1]}
        id = id.split()[0]
        path = 'channels/'
    elif param == 'sub':
        paramsVideo = {"access_token": accessToken}
        path = 'videos/'
    else:
        paramsVideo = {"access_token": accessToken, "ts": param}
        path = 'channels/'
    urlJson = requests.get('http://api.ufanet.platform24.tv/v2/' + path + id + '/stream', params=paramsVideo)
    try:
        if urlJson.json()['error']:
            xbmcgui.Dialog().ok('Внимание!', str(urlJson.json()['error']['message']))
            return
    except:
        url = urlJson.json()['hls']
    play_item = xbmcgui.ListItem(path=url)
    xbmcplugin.setResolvedUrl(_handle, True, listitem=play_item)


def router(paramstring):
    # Parse a URL-encoded paramstring to the dictionary of
    # {<parameter>: <value>} elements
    params = dict(parse_qsl(paramstring))
    if params:
        if params['action'] == 'listTvChannels':
            listCats(0, 'tv')
        elif params['action'] == 'listTvCats':
            listVideos(params['el'], 'tv')
        elif params['action'] == 'playTv':
            play_video(params['el'], '0')

        elif params['action'] == 'listArchCategories':
            listCats(params['classe'], 'arch')
        elif params['action'] == 'listArchFilmsCats':
            listArchFilms(params['el'])
        elif params['action'] == 'archViews':
            listVideos(params['film'], 'arch')
        elif params['action'] == 'playArch':
            play_video(params['el'], 'arch')

        elif params['action'] == 'listSubscriptions':
            listCats(params['sub'], 'sub')
        elif params['action'] == 'listSubsCats':
            listVideos(params['el'], 'sub')
        elif params['action'] == 'playSubs':
            play_video(params['el'], 'sub')

        elif params['action'] == 'search':
            getSearch()
        elif params['action'] == 'listProfile':
            showProfile()
        else:
            raise ValueError('Invalid paramstring: {0}!'.format(paramstring))
    else:
        list_classes()


if __name__ == '__main__':
    router(sys.argv[2][1:])
