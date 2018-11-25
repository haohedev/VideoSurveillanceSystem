# -*- coding: utf-8 -*-
import os
from eve import Eve

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
app.on_pre_POST_devices += hooks.pre_devices_post_callback
app.on_pre_PUT_devices += hooks.pre_devices_put_callback
# app.on_post_POST_devices += hooks.post_devices_post_callback
app.on_insert_devices += hooks.on_insert_devices
app.on_replace_devices += hooks.on_replace_devices

if __name__ == '__main__':
    app.run(host=host, port=port, debug=True)
