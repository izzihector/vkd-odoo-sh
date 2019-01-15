# -*- coding: utf-8 -*-

from odoo import fields, models, api


class ResCompany(models.Model):
    _inherit = "res.company"
    invoice_prefix = fields.Char(string="Invoice prefix")
    fik_id = fields.Char(string="FI Contract number")
    fik_enabled = fields.Boolean()
    fik_settings = fields.Many2one('fik.settings')
