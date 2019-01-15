# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from odoo import tools, _


class hr_employee(models.Model):
    _inherit = 'hr.employee'
    
    emp_id = fields.Char(string="Emp ID")
    rfid = fields.Char(string="RFID")
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:                    
            