# -*- coding: utf-8 -*-
{
    'name': "VK Data ApS - Contacts from CVR",

    'summary': """
        Allows you to create contacts directly from the CVR database""",

    'description': """
        This module allows you to create contacts by using their CVR number

        Remember, you need to set up the Virk.dk username and password in the
        virk.dk page of your company settings
    """,

    'author': "VK Data ApS",
    'website': "http://www.vkdata.dk",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Contacts',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': ['contacts'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/res_partner_view.xml',
        'views/res_company_view.xml',
        'views/partner_line_view.xml',
        # 'views/resources.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
    'license': 'LGPL-3',
}
