# -*- coding: utf-8 -*-
# Copyright (C) 2017 Nisus Solutions PVT LTD (<http://nisus.lk>).

{
    'name': 'Sri Lanka - Accounting',
    'version': '1.0',
    'category': 'Localization',
    'description': """
The Chart of Accounts consists of the list of all the general ledger accounts required to maintain the transactions of Sri Lanka.
	""",
    'author': 'Nisus Solutions',
    'website': 'http://nisus.lk',
    'depends': ['base_iban', 'base_vat'],
    'data': [
        'data/l10n_lk_chart_data.xml',
        'data/account.account.tag.csv',
        'data/account.account.template.csv',
        'data/account.chart.template.csv',
        'data/account.tax.template.csv',
        'data/account_chart_template_data.yml',
    ],
}
