from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    module_l10n_dk_reports_fik = fields.Boolean(string="Enable FIK module")
