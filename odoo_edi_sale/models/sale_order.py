# -*- coding: utf-8 -*-
from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'
    gln = fields.Char(string='GLN number', help='GLN identification number of the partner. This can also be called the EAN identifier/number')

    @api.multi
    def _prepare_invoice(self, context=None):
        invoice_vals = super(SaleOrder, self)._prepare_invoice()
        invoice_vals.update({
            'gln': self.gln
        })
        return invoice_vals
