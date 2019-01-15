from odoo import api, models, fields
import logging
_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):

    _inherit = 'sale.order'

    remarks = fields.Text(string="Remarks for customer", track_visibility='always')
    internal_remarks = fields.Text(string="Internal remarks", track_visibility='always')
    status_from_invoice = fields.Selection([
            ('draft','Draft'),
            ('proforma', 'Pro-forma'),
            ('proforma2', 'Pro-forma'),
            ('open', 'Open'),
            ('paid', 'Paid'),
            ('cancel', 'Cancelled'),
    ], string="Accounting Status", compute="find_invoice_status", store=True)

    @api.depends('invoice_ids', 'invoice_count', 'invoice_status')
    def find_invoice_status(self):
        for r in self:
            if r.invoice_ids:
                latest_invoice = r.invoice_ids[-1]
                r.status_from_invoice = latest_invoice.state

    @api.multi
    def _prepare_invoice(self, context=None):

        invoice_vals = super(SaleOrder, self)._prepare_invoice()
        invoice_vals.update({
            'remarks': self.remarks,
            'internal_remarks': self.internal_remarks, })
        return invoice_vals
