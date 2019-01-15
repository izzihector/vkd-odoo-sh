# -*- encoding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

# Copyright (C) 2016 VK Data ApS (<http://www.vkdata.dk>).

{
    'name': 'Denmark - Accounting',
    'version': '1.3',
    'category': 'Localization/Account Charts',
    'description': """
This is the latest Danish Odoo localization necessary to run Odoo accounting for Denmark with:
=================================================================================================
    - A chart of accounts
    - Tax structure
    - Headline/Sum accounts
    - Fiscal positions for Danish, EU and Export
    - Additional fields for notes on invoices""",
    'author': 'VK Data ApS',
    'website': 'http://www.vkdata.dk',
    'depends': ['base_iban', 'base_vat', 'contacts', 'account'],
    'data': [
        'data/account.tax.group.csv',
        'data/account.account.tag.csv',
        'data/account_chart_template.xml',
        'data/account.account.template.csv',
        'data/account.tax.template.csv',
        'data/account.chart.template.csv',
        'data/account.fiscal.position.xml',
        'data/account.fiscal.position.tax.xml',
        'data/account_chart_template.yml',
        'data/l10n_dk_forms.xml',
        'data/invoice_view.xml',
    ],
    #'demo' : ['demo/demo.xml'],
    'installable': True,
    'license': 'LGPL-3',
}
