# -*- coding: utf-8 -*-
import json,requests
from odoo import api, fields, models
from odoo import tools, _
from odoo.exceptions import Warning
from datetime import date, datetime

class set_odometer_rading(models.TransientModel):
    """set_odometer_rading"""
    _name = "set.odometer.rading"
    
    set_reading = fields.Float(string=" Last Odometer ")
    last_update_date = fields.Datetime(string="Last Update Time",default=fields.Date.to_string(datetime.now()))
    
    @api.multi
    def set_last_reading(self):
        for wiz in self:
            vehicle_obj = self.env['fleet.vehicle'].browse(self._context.get('active_id'))
            current_reading = vehicle_obj.odometer
            if current_reading > wiz.set_reading:
                raise Warning(_('Can not update the Odometer reading with less than %s. If you want to set please delete the entry from Vehicles Odometer' % (current_reading,)))
            if vehicle_obj.gps_device_id:
                param_pool = self.env['ir.config_parameter']
                api_key = str(param_pool.get_param("res.config.settings.api_key"))
                if api_key:
                    url = 'https://www.sotersat.com/api/v1.0/odometer/%s' % (vehicle_obj.gps_device_id,)
                    headers = {'Content-type': 'application/json','X-Sotersat-Api-Key': api_key}
                    api_key = str(param_pool.get_param("res.config.settings.api_key"))
                    set_data =  json.dumps({"setOdometer": wiz.set_reading})
                    r = requests.post(url, data=set_data, headers=headers)
                    data = json.loads(r.text)
                    if data.get(u'ResponseCode') == 401:
                        return {
                            'type': 'ir.actions.act_window',
                            'name': 'LogIn',
                            'res_model': 'sotersat.login.wizard',
                            'view_mode': 'form',
                            'target': 'new'
                        }
                    if not data.get(u'ResponseCode') == 200:
                        raise Warning(_('%s \n %s'  % (data.get(u'Status','Error'),data.get(u'ErrorResponse',''))))
                    vehicle_obj.write({'odometer': wiz.set_reading,'last_update_date_time': wiz.last_update_date})
                    ctx = self._context.copy()
                    ctx.update({'default_result': _('Odometer change queued to the server. It will be set as soon as the device is connected....')})
                    return {
                        'type': 'ir.actions.act_window',
                        'name': 'Success..',
                        'res_model': 'return.warning.wizard',
                        'view_mode': 'form',
                        'target': 'new',
                        'context': ctx
                    }
                else:
                    return {
                            'type': 'ir.actions.act_window',
                            'name': 'LogIn',
                            'res_model': 'sotersat.login.wizard',
                            'view_mode': 'form',
                            'target': 'new'
                        }
            else:
                raise Warning(_('There is no device Id for %s' % (vehicle_obj.name,)))
            
    @api.model
    def default_get(self, fields):
        res = super(set_odometer_rading, self).default_get(fields)
        if self._context.get('active_id',False):
            vehicle = self.env['fleet.vehicle'].browse(self._context.get('active_id'))
            res.update({'set_reading': vehicle.odometer})
        return res
        
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: