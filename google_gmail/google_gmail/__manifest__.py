# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    "name": "Google Gmail",
    "summary": "Gmail authentication support for outgoing / incoming mail servers",
    "description": """
    Google Gmail module native in version 14.0/15.0 adapted to work with version 11.0.
    Supports Google's new authentication method, as of May 30th, 2022.
    """,
    "author": "myOdoo.pl",
    "website": "https://myodoo.pl",
    "category": "Hidden",
    "version": "V11.0_1.1",
    "license": "LGPL-3",
    "depends": [
        "fetchmail",
        "mail",
        "google_account",
    ],
    "data": [
        "data/ir_config_parameter.xml",
        "views/fetchmail_server_views.xml",
        "views/ir_mail_server_views.xml"
    ],
    "installable": True,
    "auto_install": True,
}
