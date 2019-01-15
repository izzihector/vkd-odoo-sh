# -*- coding: utf-8 -*-
from odoo import models, fields, api

class ResPartner(models.Model):
    _inherit = 'res.partner'
    gln = fields.Char(string='GLN number', help='GLN identification number of the partner. This can also be called the EAN identifier/number', website_form_blacklisted=False)
