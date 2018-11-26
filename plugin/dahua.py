import json
import hashlib
from urllib.error import HTTPError

import requests


def get_cookies(ip, port, user, password):
    payload = {"method": "global.login", "params": {"userName": "", "password": "", "clientType": "Web3.0"},
               "id": 10000}
    url = f'http://{ip}:{port}/RPC2_Login'
    response = requests.post(url, data=json.dumps(payload, ensure_ascii=False))
    if response.status_code == 200:
        res_json = json.loads(response.text)
        random = res_json['params']['random']
        realm = res_json['params']['realm']
        session = res_json['session']

        password_md5 = hashlib.md5(f'{user}:{realm}:{password}'.encode()).hexdigest().upper()
        params_password_md5 = hashlib.md5(f'{user}:{random}:{password_md5}'.encode()).hexdigest().upper()

        payload['params']['userName'] = 'admin'
        payload['params']['password'] = params_password_md5
        payload['session'] = session

        response = requests.post(url, data=json.dumps(payload, ensure_ascii=False))
        if response.status_code == 200:
            res_json = json.loads(response.text)
            if not res_json['result']:
                raise HTTPError(url, res_json['error']['code'], res_json['params']['error'], None, None)
            return dict(DHLangCookie30='SimpChinese', DHVideoWHMode='Adaptive Window',
                        DhWebClientSessionID=str(session),
                        DhWebCookie=json.dumps({"username": user, "pswd": "", "talktype": 1, "logintype": 0}))


def get_device_info(ip, port, user, password):
    cookies = get_cookies(ip, port, user, password)
    session = cookies['DhWebClientSessionID']
    session = int(session) if session.isdigit() else session
    url = f'http://{ip}:{port}/RPC2'
    params = {"method": "system.multicall", "params": [
        {"method": "configManager.getConfig", "params": {"name": "General"}, "session": session, "id": 1},
        {"method": "magicBox.getDeviceType", "params": "", "session": session, "id": 2},
        {"method": "magicBox.getDeviceClass", "params": None, "session": session, "id": 3},
        {"method": "magicBox.getSerialNo", "params": "", "session": session, "id": 4},
        {"method": "configManager.getConfig", "params": {"name": "ChannelTitle"}, "session": session, "id": 5},
        {"method": "configManager.getConfig", "params": {"name": "Encode"}, "session": session, "id": 6},
        {"method": "configManager.getConfig", "params": {"name": "RTSP"}, "session": session, "id": 7},
        {"method": "LogicDeviceManager.getCameraState", "params": {"uniqueChannels": [-1]}, "session": session, "id": 8,
         "params2": ""}],
              "session": session, "id": 9}
    response = requests.post(url, data=json.dumps(params), cookies=cookies)
    response_json = json.loads(response.text)
    device_info = {
        'deviceName': response_json['params'][0]['params']['table']['MachineName'],
        'model': response_json['params'][1]['params']['type'],
        'deviceType': response_json['params'][2]['params']['type'],
        'serialNumber': response_json['params'][3]['params']['sn'],
        'protocol': {
            'name': 'rtsp',
            'port': response_json['params'][6]['params']['table']['Port']
        }
    }
    channels = []
    for i, param in enumerate(response_json['params'][4]['params']['table']):
        channels.append({k.lower(): v for k, v, in param.items()})
        if response_json['params'][7]['result']:
            states = response_json['params'][7]['params']['states']
            channels[i].update({
                'inputPort': states[i]['channel'],
                'online': states[i]['connectionState'] == 'Connected' if 'connectionState' in states[i] else False
            })
        else:
            channels[i].update({'inputPort': i + 1})
        params = response_json['params'][5]['params']['table']
        if params[i] is not None:
            for key, stream in (('mainStream', 'MainFormat'), ('subStream', 'ExtraFormat')):
                channels[i][key] = {
                    'videoEnable': params[i][stream][0]['VideoEnable'],
                    'vcodec': params[i][stream][0]['Video']['Compression'],
                    'frame': params[i][stream][0]['Video']['FPS'],
                    'audioEnable': params[i][stream][0]['AudioEnable'],
                    'acodec': params[i][stream][0]['Audio']['Compression'],
                }

    device_info['channels'] = channels
    return device_info
