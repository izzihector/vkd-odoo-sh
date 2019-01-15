from odoo import fields, models

class Website(models.Model):
    _inherit = 'website'

    website_footer = fields.Text()