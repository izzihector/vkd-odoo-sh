# -*- encoding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Denmark - Enterprise Reports',
    'version': '1.0',
    'category': 'Localization/Reports',
    'description': """
        Reports that are dependent on Odoo enterprise modules
    """,
    'author': 'VK Data ApS',
    'website': 'http://www.vkdata.dk',
    'depends': [
        'l10n_dk',
        'account',
        'account_reports'
    ],
    'data': [
        'reports/account_financial_report.xml',
        'reports/report_customer_statement.xml',
    ],
    'installable': True,
    'auto_install': False,
    'license': 'OEEL-1',
}
