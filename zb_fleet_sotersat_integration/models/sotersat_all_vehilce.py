# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo import tools, _


class sotersat_all_vehilce(models.TransientModel):
    _name = 'sotersat.all.vehilce'
#     _rec_name = 'name'
    
    iframe_url = fields.Char(string="Gpls url")
    name = fields.Char(string="Name",default='Sotersat')
    
    @api.model
    def default_get(self, fields):
        res = super(sotersat_all_vehilce, self).default_get(fields)
        param_pool = self.env['ir.config_parameter']
        api_key = str(param_pool.get_param("res.config.settings.api_key"))
        url = 'https://www.sotersat.com/webapp/odoo/%s' % (api_key,)
        res.update({'iframe_url': url})
        return  res