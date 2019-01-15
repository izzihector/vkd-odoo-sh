# -*- encoding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Denmark - Accounting Reports',
    'version': '1.0',
    'category': 'Localization/Reports',
    'description': """
        Localized reports for Denmark
    """,
    'author': 'VK Data ApS',
    'website': 'http://www.vkdata.dk',
    'depends': [
        'l10n_dk',
        'account',
    ],
    'data': [
        'views/l10n_dk_report_external_layout.xml',
        'views/l10n_dk_report_invoice_new.xml',
        'views/l10n_dk_res_config_view.xml',
        'views/chart_of_accounts_report.xml',
        'data/coa_report.xml',
        'views/l10n_dk_tax_report.xml',
        'views/l10n_dk_tax_report_eu.xml',
    ],
    'installable': True,
    'auto_install': True,
    'license': 'LGPL-3',
}
