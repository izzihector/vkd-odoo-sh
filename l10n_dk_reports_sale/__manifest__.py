# -*- encoding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Denmark - Localized Sales Reports',
    'version': '1.0',
    'category': 'Localization/Reports',
    'description': """
        Localized reports for Sales in Denmark
    """,
    'author': 'VK Data ApS',
    'website': 'http://www.vkdata.dk',
    'depends': [
        'sale',
        'l10n_dk',
        'l10n_dk_reports',
        'l10n_dk_sale'
    ],
    'data': [
        'views/l10n_dk_report_saleorder.xml',
        'views/l10n_dk_report_sale_invoice.xml',
    ],
    'installable': True,
    'auto_install': True,
    'license': 'LGPL-3',
}
