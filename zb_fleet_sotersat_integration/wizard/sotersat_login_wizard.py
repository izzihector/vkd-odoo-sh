# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo import tools, _
import json,requests
from odoo.exceptions import Warning

class sotersat_login_wizard(models.TransientModel):
    """sotersat_login_wizard."""
    _name = "sotersat.login.wizard"
    
    account = fields.Char(string="Account" , required=True)
    user_name = fields.Char(string="User",required=True)
    password = fields.Char(string="Password",required=True)
#     api_key = fields.Char(string="API Key")


    @api.multi
    def sotersat_login(self):
        for wiz in self:
            config_parameters = self.env['ir.config_parameter']
            account = wiz.account
            user = wiz.user_name
            password = wiz.password
            headers = {'Content-type': 'application/json'}
            data = {"account":account,
                    "userName":user,
                    "password":password}
            url = "https://www.sotersat.com/api/v1.0/authenticate"
            r = requests.post(url, data=json.dumps(data), headers=headers)
            authenitcated_data = json.loads(r.text)
            if authenitcated_data.get('ResponseCode','') == 200:
                api_key = authenitcated_data.get('apiKey','')
                config_parameters.set_param( "res.config.settings.api_key", api_key)
                ctx = self._context.copy()
                ctx.update({'default_result': _('API key Updated successfully...')})
                return {
                    'type': 'ir.actions.act_window',
                    'name': 'Success..',
                    'res_model': 'return.warning.wizard',
                    'view_mode': 'form',
                    'target': 'new',
                    'context': ctx
                }
            else:
                raise Warning(_('Invalid authentication details, Please try again...'))
        
    
        
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: