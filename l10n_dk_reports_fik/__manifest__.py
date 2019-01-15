# -*- encoding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

# Copyright (C) 2011 Smartmode LTD (<http://www.smartmode.co.uk>).

{
    'name': 'Denmark - Accounting FIK line',
    'version': '1.0',
    'category': 'Localization/Reports',
    'description': """
        FIK line configuration for Denmark
    """,
    'author': 'VK Data ApS',
    'website': 'http://www.vkdata.dk',
    'depends': [
        'account',
        'l10n_dk',
    ],
    'data': [
        'l10n_dk_report_invoice.xml',
        'l10n_dk_res_config_view.xml',
        'l10n_dk_fik_settings.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'license': 'LGPL-3',
}
