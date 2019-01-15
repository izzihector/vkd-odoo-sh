# -*- coding: utf-8 -*-
from odoo import models, fields, api


class ResCompany(models.Model):
    _inherit = 'res.company'
    
    bank_journal_id = fields.Many2one(
        string=u'Default Bank Journal',
        comodel_name='account.journal',
        domain="[('type', '=', 'bank')]",
        oldname="default_bank_journal_id"
    )
    
