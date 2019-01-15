# -*- encoding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Vendor Bill Email',
    'version': '1.0',
    'category': 'Customization',
    'description': """
        Module for automatic vendor bill attachment
    """,
    'author': 'VK Data ApS',
    'website': 'http://www.vkdata.dk',
    'depends': [
        'account',
        'mail',
        'document',
    ],
    'data': [
        'views/res_company_form.xml',
        'views/vendor_bill_mail_form.xml',
        'views/account_invoice_form.xml'
    ],
    'qweb': [
        'static/src/xml/pdfviewer.xml'
    ],
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
