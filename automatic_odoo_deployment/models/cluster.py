from odoo import models, fields

class OdooCluster(models.Model):
    _name = 'odoo.cluster'

    name = fields.Char()
    purpose = fields.Selection([('demo', 'Demo'),
                                ('live', 'Live'),
                                ('trial', 'Trial'),
                                ('test', 'Test'),
                                ('development', 'Development')], help="The purpose of this cluster")
    server_ids = fields.One2many('odoo.server', 'cluster_id', string="Servers")
    dns_suffix = fields.Char(help="The dns suffix will be appended to the URL of instances created in this cluster")
