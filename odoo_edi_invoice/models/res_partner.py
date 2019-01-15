# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.http import request


class ResPartner(models.Model):
    _name = 'res.partner'
    _inherit = 'res.partner'
    _description = 'Partner'
    
    bank_journal_id = fields.Many2one(
        string='Default Bank Journal',
        comodel_name='account.journal',
        domain="[('type', '=', 'bank')]",
        oldname="default_bank_journal_id"
    )
    
    odoo_edi_method = fields.Many2one(
        string='EDI Communication method',
        comodel_name='odoo_edi.endpoint',
    )
    
    odoo_edi_send_enable = fields.Boolean(
        string='Send EDI invoices to this customer',
    )

    @api.model
    def create(self, values):
        if 'gln' in values and values['gln']:
            values['odoo_edi_send_enable'] = True

        record = super(ResPartner, self).create(values)
        return record
