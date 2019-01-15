# -*- coding: utf-8 -*-
{
    'name': "Odoo EDI Invoicing",

    'summary': """
        Support for Odoo EDI Invoice send/recieve""",

    'description': """
        This module implements the functionality to send invoices and recieve vendor bills using EDI.

        This requires the Odoo EDI framework to be installed and configured
    """,

    'author': "VK Data ApS",
    'website': "https://vkdata.dk",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Accounting',
    'version': '2.0',
    'license': 'LGPL-3',

    # any module necessary for this one to work correctly
    'depends': ['account', 'account_accountant', 'odoo_edi', 'base_iban'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/account_invoice_edi_invoice_send.xml',
        'views/res_partner_form_view.xml',
        'views/res_company_form_view.xml',
        'views/res_config_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
