import time
import hashlib
from urllib.parse import urljoin
from urllib.error import HTTPError
from concurrent import futures

import requests
import xmltodict

MAX_WORKERS = 20


def time_hash():
    return hashlib.md5(str(int(time.time() * 1000)).encode('utf-8')).hexdigest()


def check_response(response):
    res_json = xmltodict.parse(response.text)
    if response.status_code != 200:
        raise HTTPError(response.url, response.status_code, res_json['ResponseStatus']['subStatusCode'], None, None)
    return res_json


def get_device_info(ip, port, user, password):
    base_url = f'http://{ip}:{port}'
    session = requests.Session()
    session.auth = (user, password)
    response = session.get(urljoin(base_url, '/ISAPI/System/deviceInfo'))
    device_info_json = check_response(response)

    urls = [urljoin(base_url, '/ISAPI/System/Video/inputs/channels'),
            urljoin(base_url, f'/ISAPI/ContentMgmt/InputProxy/channels?security=1&iv={time_hash()}'),
            urljoin(base_url, f'/ISAPI/ContentMgmt/InputProxy/channels/status?security=1&iv={time_hash()}'),
            urljoin(base_url, '/ISAPI/Security/adminAccesses')]

    workers = min(MAX_WORKERS, len(urls))
    with futures.ThreadPoolExecutor(workers) as executor:
        res = executor.map(session.get, urls)
    channels_response, digital_channels_response, digital_channels_status_response, admin_accesses_response = list(res)
    admin_accesses_json = check_response(admin_accesses_response)
    rtsp_port = next(
        protocol['portNo'] for protocol in admin_accesses_json['AdminAccessProtocolList']['AdminAccessProtocol'] if
        protocol['protocol'] == 'RTSP')

    device_info = {prop: device_info_json['DeviceInfo'].get(prop) for prop in
                   ('deviceName', 'model', 'serialNumber', 'deviceType')}
    device_info['protocol'] = {
        'name': 'rtsp',
        'port': int(rtsp_port)
    }

    if channels_response.status_code == 200:
        channels_json = xmltodict.parse(channels_response.text)
        channel_list = [
            {'name': channel['name'], 'inputPort': int(channel['inputPort'])} for channel in
            channels_json['VideoInputChannelList']['VideoInputChannel']]
        channel_len = len(channel_list)
        stream_urls = [[urljoin(base_url, f'/ISAPI/Streaming/channels/{i + 1}01/capabilities'),  # main stream
                        urljoin(base_url, f'/ISAPI/Streaming/channels/{i + 1}02/capabilities')]  # sub stream
                       for i in range(channel_len)]
        stream_urls = [y for x in stream_urls for y in x]
        workers = min(MAX_WORKERS, len(stream_urls))
        with futures.ThreadPoolExecutor(workers) as executor:
            res = list(executor.map(session.get, stream_urls))

        for i, r in enumerate(res):
            cap_json = xmltodict.parse(r.text)
            channel_list[int(i / 2)]['mainStream' if i % 2 == 0 else 'subStream'] = {
                'videoEnable': cap_json['StreamingChannel']['Video']['enabled']['#text'] == 'true',
                'vcodec': cap_json['StreamingChannel']['Video']['videoCodecType']['#text'],
                'frame': int(int(cap_json['StreamingChannel']['Video']['maxFrameRate']['#text']) / 100),
                'audioEnable': cap_json['StreamingChannel']['Audio']['enabled']['#text'] == 'true',
                'acodec': cap_json['StreamingChannel']['Audio']['audioCompressionType']['#text']
            }

    if digital_channels_response.status_code == 200:
        channels_json = xmltodict.parse(digital_channels_response.text)
        channel_list = [{'name': channel['name'], 'inputPort': 33 + index} for index, channel in
                        enumerate(channels_json['InputProxyChannelList']['InputProxyChannel'])]

    if digital_channels_status_response.status_code == 200:
        status_json = xmltodict.parse(digital_channels_status_response.text)
        for index, status in enumerate(status_json['InputProxyChannelStatusList']['InputProxyChannelStatus']):
            channel_list[index]['online'] = status['online'] == 'true'
            stream_urls = [
                [urljoin(base_url, f'/ISAPI/Event/notification/Streaming/{i + 1}01/capabilities'),  # main stream
                 urljoin(base_url, f'/ISAPI/ContentMgmt/StreamingProxy/channels/{i + 1}02/capabilitie')]  # sub stream
                for i, channel in enumerate(channel_list) if 'online' in channel and channel['online']]

        stream_urls = [y for x in stream_urls for y in x]
        workers = min(MAX_WORKERS, len(stream_urls))
        with futures.ThreadPoolExecutor(workers) as executor:
            res = list(executor.map(session.get, stream_urls))

        channel_id = -1
        for i, r in enumerate(res):
            cap_json = xmltodict.parse(r.text)
            stream_name = 'mainStream' if i % 2 == 0 else 'subStream'
            json_prefix = 'StreamingNotification' if stream_name == 'mainStream' else 'StreamingChannel'
            if i % 2 == 0:
                channel_id = int(cap_json[json_prefix]['Video']['videoInputChannelID']['#text'])
            channel_list[channel_id - 1][stream_name] = {
                'videoEnable': cap_json[json_prefix]['Video']['enabled']['#text'] == 'true',
                'vcodec': cap_json[json_prefix]['Video']['videoCodecType']['#text'],
                'frame': int(int(cap_json[json_prefix]['Video']['maxFrameRate']['#text']) / 100),
                'audioEnable': 'Audio' in cap_json[json_prefix] and cap_json[json_prefix]['Audio']['enabled'][
                    '#text'] == 'true',
                'acodec': cap_json[json_prefix]['Audio']['audioCompressionType']['#text'] if 'Audio' in cap_json[
                    json_prefix] else 'UNKOWN'
            }

    device_info['channels'] = channel_list
    return device_info
