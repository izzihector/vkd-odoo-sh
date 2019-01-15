# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2013-2014 ZestyBeanz Technologies Pvt Ltd(<http://www.zbeanztech.com>).
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
    'name': 'Fleet Sotersat Integration',
    'version': '5.1',
    'category': 'Fleet',
    'description': """
    """,
    'author': 'SOTERSAT BV Netherlands',
    'website': 'http://www.sotersat.com',
    'depends': ['fleet','base_setup','sotersat_hr','web_iframe_widget'],
    'data': [
            'security/ir.model.access.csv',
            'data/scheduler.xml',
            'security/fleet_security.xml',
            'wizard/update_odometer_view.xml',
            'wizard/odometer_update_sucess.xml',
            'wizard/odometer_refresh.xml',
            'wizard/set_odometer_reading.xml',
            'wizard/condition_check_success.xml',
            'wizard/return_warning_wizard.xml',
            'wizard/update_trip_wizard_view.xml',
            'wizard/sotersat_login_wizard_view.xml',
            'wizard/trip_gps_display_view.xml',
            'view/fleet_view.xml',
            'view/sotersat_all_vehilce.xml',
            'view/sotersat_trip_details.xml',
            'res_config_view.xml',
            'menu.xml'
        ],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
    'application': True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: