{
    'name': 'Server Info',
    'summary': 'Settings tab with automatically updated server informations',
    'description': '''
    This module add new tab 'Server Info' in settings.
    This tab contains automatically updated informations about server cpu, ram and disk usage.
    It also allows you to change frequency of informations updates.
    ''',
    'author': 'myOdoo.pl',
    'website': 'https://myodoo.pl',
    'category': 'Technical',
    'version': '1.0.2',
    'license': 'LGPL-3',
    'images': ['static/description/banner.png', 'static/description/usage.png'],
    'external_dependencies': {
        "python": ["psutil"]
    },
    'depends': [
        'base_setup',
        'web'
    ],
    'data': [
        'views/fields.xml',
        'data/settings_records.xml'
    ],
    'qweb': [
        'static/src/xml/auto_update.xml',
        'description/usage.png'
    ],
    'assets': {
        'web.assets_backend': [
            '/server_info/static/js/auto_update.js'
        ]
    },
    'installable': True,
    'auto_install': False
}
