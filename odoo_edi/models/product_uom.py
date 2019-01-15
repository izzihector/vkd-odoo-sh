# -*- coding: utf-8 -*-
from odoo import models, fields, api


class ProductUom(models.Model):
    _inherit = 'product.uom'
    edi_name = fields.Many2one('odoo_edi.product.uom', string="EDI Unit name", help="The generic EDI unit name used for correctly handling EDI invoicing")

