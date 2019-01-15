
from odoo import models, fields, api

class ResCompany(models.Model):
    _inherit = "res.company"

    virk_user = fields.Char(string="Virk.dk Username")
    virk_pass = fields.Char(string="Virk.dk Password")
