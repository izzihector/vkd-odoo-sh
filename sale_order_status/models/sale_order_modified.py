# -*- coding: utf-8 -*-

from odoo import models, fields

class SaleOrderStatus(models.Model):
    _name = 'sale.order'
    _inherit = "sale.order"

    technician_id = fields.Many2one('hr.employee', string='Responsible')
    order_status_id = fields.Many2one('sale.order.status', string='Progress', widget="selection")





