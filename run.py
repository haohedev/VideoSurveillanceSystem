# -*- coding: utf-8 -*-
import os

from eve import Eve
from eve_swagger import swagger

import hooks

if 'PORT' in os.environ:
    port = int(os.environ.get('PORT'))
    # use '0.0.0.0' to ensure your REST API is reachable from all your
    # network (and not only your computer).
    host = '0.0.0.0'
else:
    port = 5000
    host = '127.0.0.1'

app = Eve()
app.register_blueprint(swagger)
app.on_pre_POST_devices += hooks.pre_devices_post_callback
app.on_pre_PUT_devices += hooks.pre_devices_put_callback
# app.on_post_POST_devices += hooks.post_devices_post_callback
app.on_insert_devices += hooks.on_insert_devices
app.on_replace_devices += hooks.on_replace_devices

app.config['SWAGGER_INFO'] = {
    'title': '视频集成HTTP API',
    'version': '1.0',
    'description': '通过接口添加DVR、NVR、IPC等设备,添加成功后返回通道的信息并且开始采集视频到SRS中',
    'contact': {
        'name': 'HaoHe',
        'email': 'hao.he@foxmail.com'
    },
    'schemes': ['http', 'https'],
}

if __name__ == '__main__':
    app.run(host=host, port=port, debug='DEBUG' in os.environ)
