# -*- coding: utf-8 -*-
{
    'name': "Bank Import Multi Currency",

    'summary': """
        Import Bank Statements with multiple currencies""",

    'description': """
        Enables you to import bank statements with multiple currencies
    """,

    'author': "VK Data ApS",
    'website': "http://www.vkdata.dk",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Accounting',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': ['account'],

    # always loaded
    'data': [
        'views/account_view.xml',
    ],
}
