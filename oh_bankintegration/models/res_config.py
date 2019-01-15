# -*- coding: utf-8 -*-

import time
import datetime
from dateutil.relativedelta import relativedelta

import odoo
from odoo import SUPERUSER_ID
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    # api_key = fields.Char(string=_('API key'), help="Enter API key here")
    payment_margin = fields.Integer(
        string=_('Payment Margin'), help="Payment Margin", default=0)
    autopay = fields.Boolean(string=_('Default auto pay'), default=False)
    payment_journal = fields.Many2one(
        'account.journal', string='Payment journal', domain=[('type', '=', 'bank')])
    multiple_payment_type = fields.Selection([(1, 'Pay each separately'), (2, 'Pay national and international collected in one single payment'), (
        3, 'Pay only international collected in one single payment')], string='If multiple payments to same customer on one day', default=1)

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        get_param = self.env['ir.config_parameter'].sudo().get_param
        payment_journal = get_param('payment_journal')
        res.update(
            payment_margin=int(get_param('payment_margin')),
            autopay=False if get_param('autopay') == 'False' else True,
            payment_journal=int(
                payment_journal) if payment_journal != '0' else 0,
            multiple_payment_type= 1
        )
        return res

    @api.multi
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        set_param = self.env['ir.config_parameter'].sudo().set_param
        # we store the repr of the values, since the value of the parameter is
        # a required string
        try:
            set_param('payment_margin', repr(self.payment_margin))
            set_param('autopay', repr(self.autopay))
            set_param('payment_journal', repr(
                self.payment_journal.id if self.payment_journal else 0))
        except Exception as e:
            print(str(e))
