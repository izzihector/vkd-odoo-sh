from odoo import api, fields, models


class AccountConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    default_bank_journal_id = fields.Many2one(
        string=u'Default Bank Journal',
        comodel_name='account.journal',
        related='company_id.bank_journal_id'
    )

    default_odoo_edi_method = fields.Many2one(
        string=u'Default EDI Method',
        comodel_name='odoo_edi.endpoint',
        default_model='res.partner',
    )
