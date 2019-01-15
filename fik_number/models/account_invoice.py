# -*- coding: utf-8 -*-
from odoo import fields, api, models, _

import logging
_logger = logging.getLogger(__name__)

class AccountInvoice(models.Model):
    _name = "account.invoice"
    _inherit = ["account.invoice"]

    fik_number = fields.Char(string="FIK Number", default='', readonly=True)
