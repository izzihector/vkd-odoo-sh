# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2018-     Odoo House (<https://odoohouse.dk>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': 'Odoo Vendor Bill FIK Number',
    'version': '1.0',
    'category': 'Tools',
    'description': """
Odoo Vendor Bill FIK Number.
=================================
This module share FIK number.
""",
    'author': 'Danish FIK number',
    'website': 'http://odoo.com',
    'summary': 'Odoo Vendor Bill FIK Number',
    'sequence': 20,
    'depends': ['base', 'account'],
    'data': [
        'views/account_invoice_view.xml',
    ],
    'demo': [
    ],
    'test': [
    ],
    'css': [
    ],
    'images': [
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
