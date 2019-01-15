# -*- coding: utf-8 -*-
{
    'name': "Odoo EDI Inventory integration",

    'summary': """
        Create necessary menus and views that can be used when inventory management is installed""",

    'description': """
        Long description of module's purpose
    """,

    'author': "VK Data ApS",
    'website': "https://vkdata.dk",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Warehouse',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': ['odoo_edi', 'stock'],
    'auto_install': True,

    'license': 'LGPL-3',

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/product_edi_uom_views.xml',
    ],
}
