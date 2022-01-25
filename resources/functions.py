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


def randomIcon(path):
    file = random.choice(os.listdir(path + "/resources/icons/"))
    filePath = path + '/resources/icons/' + file
    return filePath
