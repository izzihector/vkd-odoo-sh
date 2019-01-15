from odoo import models, fields, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    default_port_number = fields.Integer(default_model='odoo.instance', help="The default port number set on new instances")
    use_load_balancing = fields.Boolean(help="Evenly distribute new instances across servers in a cluster")

    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res.update(
            use_load_balancing=self.env['ir.config_parameter'].sudo().get_param('automatic_odoo_deployment.use_load_balancing')
        )
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param('automatic_odoo_deployment.use_load_balancing', self.use_load_balancing)