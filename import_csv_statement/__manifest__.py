# -*- coding: utf-8 -*-

{
    'name': 'Import CSV Statement',
    'version': '1.1',
    'category': 'Account',
    'description': """
This module provides import csv bank statement.
====================================================================================

    """,
    'author': 'VK Data ApS',
    'website': 'https://vkdata.dk',
    'depends': ['account'],
    'data': [
        'views/account_custom_view.xml',
        'wizard/import_csv_statement.xml',
    ],
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
