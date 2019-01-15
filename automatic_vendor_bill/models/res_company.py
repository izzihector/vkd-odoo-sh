from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)


class ResCompany(models.Model):
    _inherit = 'res.company'

    vendor_bill_alias = fields.Many2one('vendor.bill.mail')
