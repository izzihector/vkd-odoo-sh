from odoo import models, fields, api

class MailMailStatistics(models.Model):
    _inherit = 'mail.mail.statistics'

    recipient = fields.Char(compute='_compute_recipient', store=True)

    @api.depends('res_id', 'model')
    def _compute_recipient(self):
        super(MailMailStatistics, self)._compute_recipient()