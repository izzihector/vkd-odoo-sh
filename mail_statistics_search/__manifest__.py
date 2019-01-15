# -*- coding: utf-8 -*-

{
    'name': 'Mail statistics search',
    'version': '1.0',
    'category': 'Mail',
    'description': """
    Adds recipient field to mail statistics search
    """,
    'author': 'VK Data ApS',
    'website': 'https://vkdata.dk',
    'depends': ['mass_mailing'],
    'data': [
        'views/mail_statistics_search_view.xml'
    ],
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}