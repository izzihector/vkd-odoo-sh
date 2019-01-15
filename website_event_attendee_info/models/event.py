from odoo import api, fields, models

class EventRegistration(models.Model):
    _inherit = 'event.registration'

    company = fields.Char(string="Company", required=True)
    email = fields.Char(string='Email', required=True)
    phone = fields.Char(string='Phone', required=True)