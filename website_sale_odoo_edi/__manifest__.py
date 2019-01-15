# -*- coding: utf-8 -*-
{
    'name': "Odoo EDI eCommerce Integration",

    'summary': """
        Create necessary fields and behaviour to support the usage of order checkouts using EDI""",

    'description': """
        Create necessary fields and behaviour to support the usage of order checkouts using EDI

        - GLN-number field on checkout for address information
        - Pay using EDI (Payment Method)
        - Automatic configuration of customer to get invoices through EDI

        In order for this to work properly on the website and actually display the `gln` field, you need to find the ID of the  `gln` field under Settings -> Technical -> Database structure -> Fields

        When you have the ID run the following query directly in PostgreSQL

        ```
        UPDATE public.ir_model_fields SET website_form_blacklisted=false WHERE id = <ID of the field>
        ```

        Fx. if the ID is 3711, then the query would be:

        ```
        UPDATE public.ir_model_fields SET website_form_blacklisted=false WHERE id = 3711
        ```

        Restart the Odoo instance now it should be working
    """,

    'author': "VK Data ApS",
    'website': "https://vkdata.dk",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Website',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': ['odoo_edi', 'odoo_edi_sale', 'website_sale', 'website_form'],

    'license': 'LGPL-3',

    # always loaded
    'data': [
        #'security/ir.model.access.csv',
        'views/templates.xml',
    ],
}
