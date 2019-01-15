# -*- coding: utf-8 -*-
{
    'name': "Odoo EDI Sales",

    'summary': """
        Support for Odoo EDI Sales orders and qoutations""",

    'description': """
        This module implements the functionality to handle sales orders and qoutations using EDI.

        This requires the Odoo EDI framework to be installed and configured
    """,

    'author': "VK Data ApS",
    'website': "https://vkdata.dk",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Sales',
    'version': '1.0',
    'license': 'LGPL-3',

    # any module necessary for this one to work correctly
    'depends': ['sale', 'odoo_edi_invoice', 'odoo_edi'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        #'views/account_invoice_edi_invoice_send.xml',
        #'views/res_partner_form_view.xml',
        #'views/res_company_form_view.xml',
        #'views/res_config_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        #'demo/demo.xml',
    ],
}
