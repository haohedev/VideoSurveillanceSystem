from urllib.error import HTTPError

from flask import abort
from flask import g

import plugin


def get_device_info(_type, ip, port, user, password):
    return getattr(plugin, _type).get_device_info(ip, port, user, password)


def devices_callback(request):
    body = request.json
    try:
        g.device_info = get_device_info(body['type'], body['address']['ip'], body['address']['port'], body['user'],
                                        body['password'])
    except HTTPError as e:
        abort(e.code, e.reason)
    except Exception as e:
        abort(422, str(e))


def pre_devices_post_callback(request):
    devices_callback(request)


def pre_devices_put_callback(request, _):
    devices_callback(request)


def on_insert_devices(items):
    items[0].update(g.device_info)


def on_replace_devices(updates, original):
    updates.update(g.device_info)
