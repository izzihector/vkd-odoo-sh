# See LICENSE file for full copyright and licensing details.
from odoo import models, fields, api


class ResCompany(models.Model):
    _inherit = 'res.company'

    aad_oauth_enabled = fields.Boolean(string='Allow users to connect with Office 365')
    aad_enable_webhooks = fields.Boolean(string='Enable WebHooks')
    aad_oauth_client_id = fields.Char(string='Application Id')
    aad_oauth_client_secret = fields.Char(string='Password')

    @api.multi
    def write(self, vals):
        to_update = []

        for company in self:
            if 'aad_enable_webhooks' in vals and vals['aad_enable_webhooks'] != company.aad_enable_webhooks:
                to_update.append(company)

        res = super(ResCompany, self).write(vals)

        for company in to_update:
            if company.aad_enable_webhooks:
                self.env['azure.ad.user'].search([]).init_webhook()
            else:
                self.env['azure.ad.user'].search([]).remove_webhook()

        return res

    @api.onchange('aad_oauth_enabled')
    def onchange_aad_oauth_enabled(self):
        if not self.aad_oauth_enabled:
            self.env['azure.ad.user'].unlink()
