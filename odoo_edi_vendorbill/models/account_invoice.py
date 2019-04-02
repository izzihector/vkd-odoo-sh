from odoo import models, fields

class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    edi_vendor_bill_total = fields.Monetary(
        string='Invoice total from EDI', readonly=True)
    edi_vendor_bill_total_untaxed = fields.Monetary(
        string='Invoice subtotal from EDI', readonly=True)
