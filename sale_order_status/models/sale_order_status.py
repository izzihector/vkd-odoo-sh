# -*- coding: utf-8 -*-

from odoo import models, fields

class SaleOrderStatus(models.Model):
    _name = 'sale.order.status'

    name = fields.Char(string="Name", required=True)


