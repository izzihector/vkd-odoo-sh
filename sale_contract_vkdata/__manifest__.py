# -*- coding: utf-8 -*-
{
    'name': "VK Data ApS - Extension for subscription management",

    'summary': """
        Extend Subscription management with company specific login""",

    'description': """
        Extends the Odoo Subscription management (sale_contract) application with company specifc business logic for subscription management
    """,

    'author': "VK Data ApS",
    'website': "http://www.vkdata.dk",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Sales',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': ['sale_subscription'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/vkdata_sale_subscription_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
