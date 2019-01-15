from odoo import models, fields, api
from odoo.exceptions import ValidationError

class OdooServer(models.Model):
    _name = 'odoo.server'

    name = fields.Char(help="Name of the server")
    cluster_id = fields.Many2one('odoo.cluster', help="Choose which shared resource cluster the server is part of. Empty is treated as a dedicated server")
    instance_ids = fields.One2many('odoo.instance', 'server_id', string="Instances")
    max_instances = fields.Integer(default=-1, help="The maximum number of instances allowed on this server. Default is -1 which is unlimited.")
    ip_address = fields.Char(string="IP-Address", help="IP Address of the server")
    admin_username = fields.Char(help="The server administrator username")
    admin_password = fields.Char(help="The server administrator password")
    use_ssh_keys = fields.Boolean(help="Use SSH keys to contact github during deployment")
    ssl_certificate = fields.Boolean(string="Has SSL Certificate?", help="Check this if the server has a valid SSL certificate")
    partner_id = fields.Many2one('res.partner', string="Customer", help="The partner this server belongs to, if it is a dedicated server")

    @api.onchange('cluster_id')
    def _set_partner_id(self):
        if self.cluster_id:
            self.partner_id = False

    @api.constrains('cluster_id')
    def _check_partner_id(self):
        for r in self:
            if not r.cluster_id and not r.partner_id:
                raise ValidationError("Please select a partner")