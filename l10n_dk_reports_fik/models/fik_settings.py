from odoo import api, fields, models

class FikSettings(models.Model):
    _name = 'fik.settings'

    name = fields.Char()
    customer_code_length = fields.Integer()
    invoice_number_length = fields.Integer()
