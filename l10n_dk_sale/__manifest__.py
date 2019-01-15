# -*- encoding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

# Copyright (C) 2016 VK Data ApS (<http://www.vkdata.dk>).

{
    'name': 'Denmark - Sales Extension',
    'version': '1.3',
    'category': 'Localization',
    'description': """
This module extends the Odoo sales application with new features specific for Denmark as well as integrates it with the existing Danish Localization:
=================================================================================================""",
    'author': 'VK Data ApS',
    'website': 'http://www.vkdata.dk',
    'depends': ['l10n_dk', 'sale'],
    'data': [
        'data/sale_view.xml',
        'views/sale_order_view.xml'
    ],
    #'demo' : ['demo/demo.xml'],
    'installable': True,
    'auto_install': True,
    'license': 'LGPL-3',
}
