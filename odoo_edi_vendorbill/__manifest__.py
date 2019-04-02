# -*- coding: utf-8 -*-
{
    'name': "EDI Vendor Bills (Recieve EDI invoices) ",

    'summary': """
       Support for Odoo EDI Vendor Bills recieve""",

    'description': """
        This module implements the functionality to receive vendor bills using EDI.
        This requires the Odoo EDI framework to be installed and configured
    """,

    'author': "VK DATA ApS",
    'website': "https://vkdata.dk",

    'category': 'Accounting',
    'version': '1.1',

    # any module necessary for this one to work correctly
    'depends': ['odoo_edi', 'odoo_edi_invoice'],

    # always loaded
    'data': [
        'data/ir_cron.xml',
        'views/account_invoice_views.xml',
    ],
}
