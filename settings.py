# -*- coding: utf-8 -*-
import os

MONGO_URI = os.environ.get('MONGODB_URI', 'mongodb://localhost:27017/video')

RESOURCE_METHODS = ['GET', 'POST', 'DELETE']

ITEM_METHODS = ['GET', 'PUT', 'DELETE']

devices = {
    'item_title': 'devices',

    # 'additional_lookup': {
    #     'url': 'regex("[\w]+")',
    #     'field': 'lastname'
    # },

    # Schema definition, based on Cerberus grammar. Check the Cerberus project
    # (https://github.com/pyeve/cerberus) for details.
    'schema': {
        'address': {
            'type': 'dict',
            'required': True,
            'unique': True,
            'schema': {
                'ip': {'type': 'string',
                       'regex': r'(?=(\b|\D))(((\d{1,2})|(1\d{1,2})|(2[0-4]\d)|(25[0-5]))\.){3}'
                                r'((\d{1,2})|(1\d{1,2})|(2[0-4]\d)|(25[0-5]))(?=(\b|\D))'},
                'port': {'type': 'integer', 'required': True}
            }

        },
        'user': {
            'type': 'string',
            'required': True
        },
        'password': {
            'type': 'string',
            'required': True
        },
        'type': {
            'type': 'string',
            'allowed': ['hikvision', 'dahua', 'ivms_8700'],
            'required': True
        },
        'deviceName': {
            'type': 'string',
            'readonly': True,

        },
        'model': {
            'type': 'string',
            'readonly': True,
        },
        'serialNumber': {
            'type': 'string',
            'readonly': True,
        },
        'deviceType': {
            'type': 'string',
            'readonly': True,
        },
        'protocol': {
            'type': 'dict',
            'readonly': True,
            'schema': {
                'name': {'type': 'string'},
                'port': {'type': 'integer'}
            }
        },
        'channels': {
            'type': 'list',
            'readonly': True,
            'schema': {
                'inputPort': {'type': 'string'},
                'name': {'type': 'string'},
                'mainStream': {
                    'type': 'dict',
                    'schema': {
                        'videoEnable': {'type': 'boolean'},
                        'vcodec': {'type': 'string'},
                        'frame': {'type': 'integer'},
                        'audioEnable': {'type': 'boolean'},
                        'acodec': {'type': 'string'}
                    }
                },
                'subStream': {
                    'type': 'dict',
                    'schema': {
                        'videoEnable': {'type': 'boolean'},
                        'vcodec': {'type': 'string'},
                        'frame': {'type': 'integer'},
                        'audioEnable': {'type': 'boolean'},
                        'acodec': {'type': 'string'}
                    }
                }
            }
        }
    }
}

DOMAIN = {
    'devices': devices
}
