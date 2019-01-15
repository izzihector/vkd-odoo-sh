from odoo import api, fields, models


class AccountConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    invoice_prefix = fields.Char(string="Invoice prefix *", related="company_id.invoice_prefix")
    fik_id = fields.Char(string="FI Contract number *", related="company_id.fik_id")
    fik_enabled = fields.Boolean(string="Show FIK on invoice *", related="company_id.fik_enabled")
    fik_settings = fields.Many2one('fik.settings', string="FIK line configuration *", related="company_id.fik_settings")
