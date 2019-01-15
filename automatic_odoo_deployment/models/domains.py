from odoo import models, fields, api

class OdooInstanceDomain(models.Model):
    _name = 'odoo.instance.domains'

    name = fields.Char(string="URL")
    description = fields.Char()
    instance_id = fields.Many2one('odoo.instance')