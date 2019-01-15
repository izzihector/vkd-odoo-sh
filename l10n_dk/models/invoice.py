from odoo import fields, models


class AccountInvoice(models.Model):

    _inherit = 'account.invoice'

    remarks = fields.Text(string="Remarks", track_visibility='always')
    internal_remarks = fields.Text(string="Internal remarks", track_visibility='always')
