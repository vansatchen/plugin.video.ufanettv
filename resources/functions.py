import sys
import xbmcgui, xbmcplugin, xbmcaddon, xbmcvfs, xbmc
import uuid
import os, random
import requests

addonPath = xbmcvfs.translatePath(xbmcaddon.Addon(id='plugin.video.ufanettv').getAddonInfo('path'))
profilePath = xbmcvfs.translatePath(xbmcaddon.Addon(id='plugin.video.ufanettv').getAddonInfo('profile'))

def checkSettings(handle):
    # Get credentials from settings
    contractLogin = xbmcplugin.getSetting(handle, "loginStr")
    contractPassword = xbmcplugin.getSetting(handle, "passStr")

    if not contractLogin or not contractPassword:
        # if settings empty, show warning and settings window
        xbmcgui.Dialog().notification('Ошибка авторизации', 'Введите корректные данные.', xbmcgui.NOTIFICATION_ERROR)
        xbmcaddon.Addon().openSettings()
        sys.exit()


def generateUUID(_handle):
    deviceID = str(uuid.uuid4())
    getToken = requests.post('http://api.ufanet.platform24.tv/v2/auth/device', json={"device_id": deviceID})
    for el in getToken.json():
        if el == 'error_code':
            contractLogin = xbmcplugin.getSetting(_handle, "loginStr")
            contractPassword = xbmcplugin.getSetting(_handle, "passStr")
            getToken = requests.post('http://api.ufanet.platform24.tv/v2/auth/login', json={"login": contractLogin, "password": contractPassword})
            try:
                if getToken.json()['error']:
                    xbmcgui.Dialog().ok('Внимание!', str(getToken.json()['error']['message']))
                    sys.exit()
            except:
                pass
            # Get token
            accessToken = getToken.json()['access_token']
            # Register device
            jsonData = {'vendor': xbmc.getInfoLabel('System.FriendlyName'),
                        'model': xbmc.getInfoLabel('System.BuildVersion').split()[0],
                        'serial': deviceID,
                        'device_type': 'tv',
                        'version': xbmc.getInfoLabel('System.AddonVersion("plugin.video.ufanettv")'),
                        'application_type': 'android-mobile'}
            postDevice = requests.post('http://api.ufanet.platform24.tv/v2/users/self/devices?access_token=' + accessToken, json=jsonData)
            # Get new devicesID
            try:
                if postDevice.json()['error']:
                    xbmcgui.Dialog().ok('Внимание!', str(postDevice.json()['error']['message']))
                    paramsChan = {"access_token": accessToken}
                    getDevices = requests.get('http://api.ufanet.platform24.tv/v2/users/self/devices', params=paramsChan)
                    devices = []
                    devicesLst = []
                    indexInt = 0
                    for elem in getDevices.json():
                        index = ['index', indexInt]
                        id = ['id', elem['id']]
                        deviceType = ['deviceType', elem['device_type']]
                        vendor = ['vendor', elem['vendor']]
                        model = ['model', elem['model']]
                        loginAt = ['login_at', elem['login_at']]
                        device = [index, id, deviceType, vendor, model, loginAt]
                        devices.append(dict(device))
                        indexInt += 1
                    for elm in devices:
                        device = str(elm['deviceType']) + ": " + str(elm['vendor']) + " - " + str(elm['model']) + "  " + str(elm['login_at'])
                        devicesLst.append(device)

                    removeDev = xbmcgui.Dialog().select('Выберите устройство для удаления', devicesLst)
                    for device in devices:
                        if device['index'] == int(removeDev):
                            requests.delete('http://api.ufanet.platform24.tv/v2/users/self/devices/' + device['id'], params=paramsChan)
                            contractLogin = xbmcplugin.getSetting(_handle, "loginStr")
                            contractPassword = xbmcplugin.getSetting(_handle, "passStr")
                            getToken = requests.post('http://api.ufanet.platform24.tv/v2/auth/login', json={"login": contractLogin, "password": contractPassword})
                            # Get token
                            accessToken = getToken.json()['access_token']
                            # Register device
                            jsonData = {'vendor': xbmc.getInfoLabel('System.FriendlyName'),
                                        'model': xbmc.getInfoLabel('System.BuildVersion').split()[0],
                                        'serial': deviceID,
                                        'device_type': 'tv',
                                        'version': xbmc.getInfoLabel('System.AddonVersion("plugin.video.ufanettv")'),
                                        'application_type': 'android-mobile'}
                            postDevice = requests.post('http://api.ufanet.platform24.tv/v2/users/self/devices?access_token=' + accessToken, json=jsonData)
                            deviceID = postDevice.json()['id']
            except:
                deviceID = postDevice.json()['id']

    file = open(profilePath + 'DeviceID.txt', 'w')
    file.write(deviceID)
    file.close()
    return deviceID


def checkDeviceID(_handle):
    try:
        file = open(profilePath + 'DeviceID.txt', 'r')
        deviceID = file.readline()
        if deviceID.strip() == "":
            file.close()
            deviceID = generateUUID(_handle)
        else:
            file.close()
    except OSError:
        deviceID = generateUUID(_handle)
    return deviceID


def channelFunc(channelsData):
    channels = []
    for elem in channelsData:
        name = ['name', elem['name']]
        thumb = ['thumb', elem['icon']]
        genre = ['genre', 'TV channel']
        id = ['id', elem['id']]
        video = ['video', elem['id']]
        channel = [name, thumb, video, genre, id]
        channels.append(dict(channel))
    return channels


def filmFunc(filmsData):
    films = []
    filmsData = [filmsData]
    for elem in filmsData:
        name = ['name', elem['title']]
        thumb = ['thumb', elem['img'][0]['src'] + '?w=462&h=261&crop=true']
        genre = ['genre', ' '.join([ele['name'] for ele in elem['genres']])]
        id = ['id', elem['id']]
        video = ['video', elem['id']]
        film = [name, thumb, video, genre, id]
        films.append(dict(film))
    return films


def thumbForGenre(label):
    if label == 'Новинки': thumb = addonPath + 'resources/icons/genres/new.png'
    elif label == 'Зарубежные': thumb = addonPath + 'resources/icons/genres/zarub.png'
    elif label == 'Российские': thumb = addonPath + 'resources/icons/genres/russian.png'
    elif label == 'СССР': thumb = addonPath + 'resources/icons/genres/ussr.png'
    elif label == 'Лучшие' or label == 'Лучшее': thumb = addonPath + 'resources/icons/genres/best.png'
    elif label == 'Драма': thumb = addonPath + 'resources/icons/genres/drama.png'
    elif label == 'Комедия': thumb = addonPath + 'resources/icons/genres/comedy.png'
    elif label == 'Триллер': thumb = addonPath + 'resources/icons/genres/triller.png'
    elif label == 'Мелодрама': thumb = addonPath + 'resources/icons/genres/heart.png'
    elif label == 'Детектив': thumb = addonPath + 'resources/icons/genres/detective.png'
    elif label == 'Фантастика': thumb = addonPath + 'resources/icons/genres/fantastic.png'
    elif label == 'Фэнтези': thumb = addonPath + 'resources/icons/genres/fantasy.png'
    elif label == 'Приключения': thumb = addonPath + 'resources/icons/genres/adventure.png'
    elif label == 'Боевик': thumb = addonPath + 'resources/icons/genres/boevic.png'
    elif label == 'Военный': thumb = addonPath + 'resources/icons/genres/war.png'
    elif label == 'Ужасы': thumb = addonPath + 'resources/icons/genres/horror.png'
    elif label == 'История': thumb = addonPath + 'resources/icons/genres/history.png'
    elif label == 'Музыка': thumb = addonPath + 'resources/icons/genres/music.png'
    elif label == 'Документальные': thumb = addonPath + 'resources/icons/genres/documental.png'
    elif label == 'Мультсериалы': thumb = addonPath + 'resources/icons/genres/documental.png'
    elif label == 'Мультфильмы': thumb = addonPath + 'resources/icons/genres/documental.png'
    elif label == 'Сериалы': thumb = addonPath + 'resources/icons/serial.png'
    elif label == 'Сказка': thumb = addonPath + 'resources/icons/genres/fantasy.png'
    elif label == 'Фильмы': thumb = addonPath + 'resources/icons/genres/documental.png'
    elif label == 'Путешествия': thumb = addonPath + 'resources/icons/genres/adventure.png'
    elif label == 'Юмор': thumb = addonPath + 'resources/icons/genres/comedy.png'
    else: thumb = addonPath + 'resources/icons/genres/documental.png'
    return thumb


#def randomIcon(path):
#    file = random.choice(os.listdir(path + "/resources/icons/"))
#    filePath = path + '/resources/icons/' + file
#    return filePath


#def get_url(**kwargs):
#    return '{0}?{1}'.format(_url, urlencode(kwargs))


#def getTvCats(accessToken):
#    paramsChan = {"includes": "images.whiteback", "access_token": accessToken}
#    getChannels = requests.get('http://api.ufanet.platform24.tv/v2/channels/categories', params=paramsChan)
#    TVCHANNELS = {}
#    for cat in getChannels.json():
#        TVCHANNELS[cat['name']] = channelFunc(cat['channels'])
#    return TVCHANNELS


#def getTvVideos(category):
#    someList = []
#    someDict = {}
#    for el in category[2:-1].replace('},', '').replace('}', '').split('{'):
#        elList = []
#        for ele in el.replace('\'', '').strip().split(', '):
#            elList.append(ele.split(': '))
#        someList.append(dict(elList))
#    return someList


#def getArchViews(film, accessToken):
#    paramsView = {'access_token': accessToken}
#    getView = requests.get('http://api.ufanet.platform24.tv/v2/programs/' + film + '/schedule', params=paramsView)
#    return getView.json()



# Experiment:
def showProfile():
    window = xbmcgui.WindowDialog()
    window.addControl(xbmcgui.ControlImage(x=25, y=25, width=150, height=150, filename=addonPath + 'resources/icons/profile.png'))
#    window.doModal()
    window.show()
    xbmc.sleep(1000)
    window.close()


def getSearch():
    searchValue = xbmcgui.Dialog().input('Поиск', type=xbmcgui.INPUT_ALPHANUM)
    if not searchValue:
        list_classes()
    searchResults = []
    # Get all channels
    paramsChan = {"includes": "images.whiteback", "access_token": accessToken}
    getChannels = requests.get('http://api.ufanet.platform24.tv/v2/channels/categories', params=paramsChan)
    for el in getChannels.json()[0]['channels']:
        if searchValue.lower() in el['name'].lower():
            searchResults.append(el)
    # Search for videos in archive and streams
    paramsSearch = {'access_token': accessToken, 'text': searchValue}
    getVideos = requests.get('http://api.ufanet.platform24.tv/v2/search', params=paramsSearch)
    for ele in getVideos.json():
        searchResults.append(ele['video'])
    listSearch(searchResults)


def listSearch(results):
    xbmcplugin.setPluginCategory(_handle, 'Поиск')
    xbmcplugin.setContent(_handle, 'videos')
    if not results: return
    for result in results:
        try:
            if result['title']:
                list_item = xbmcgui.ListItem(label=result['title'] + '    Источник: ' + result['source']['title'])
                list_item.setInfo('video', {'title': result['title'], 'mediatype': 'video'})
                list_item.setArt({'thumb': result['img'][0]['src'], 'fanart': result['source']['img']})
                url = get_url(action='playSubs', sub=result['id'])
        except: pass
        try:
            if result['name']:
                list_item = xbmcgui.ListItem(label=result['name'])
                list_item.setInfo('video', {'title': result['name'], 'mediatype': 'video'})
                url = get_url(action='play', video=result['id'])
        except: pass
        list_item.setProperty('IsPlayable', 'true')
        is_folder = False
        xbmcplugin.addDirectoryItem(_handle, url, list_item, is_folder)
    xbmcplugin.endOfDirectory(_handle)
