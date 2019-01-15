# -*- coding: utf-8 -*-
{
    'name': "sale_order_status",

    'summary': """
        this module had modified order form with a new module an d order id and technician id fields.""",

    'description': """
        this module had modified order form with a new module an d order id and technician id fields.
    """,

    'author': "Nisus Solutions",
    'website': "http://www.nisus.lk",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'sales',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/sale_order_status_view.xml',
        'views/sale_order_modified_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}