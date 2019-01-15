# -*- coding: utf-8 -*-
{
    'name': "Automatic Odoo Deployment",

    'summary': """
        This module handles the creation of Odoo instances""",

    'description': """
        This module adds all views, models, and methods, necessary for the deployment of new Odoo instances
        on our shared resource servers, from an already installed Odoo.
    """,

    'author': "VK Data ApS",
    'website': "https://vkdata.dk",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['sale_subscription', 'contacts'],
    'data': [
        'security/security.xml',
        'views/cluster_views.xml',
        'views/server_views.xml',
        'views/instance_views.xml',
        'views/res_config_view.xml',
        'views/res_partner_view.xml',
        'security/ir.model.access.csv',
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
}