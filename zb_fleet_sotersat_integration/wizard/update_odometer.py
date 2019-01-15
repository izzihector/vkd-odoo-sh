# -*- coding: utf-8 -*-
import json,requests
from odoo import api, fields, models
from odoo import tools, _
from odoo.exceptions import Warning
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from datetime import date, datetime

class update_odometer(models.TransientModel):
    """update_odometer"""
    _name = "update.odometer"
    
    
    @api.multi
    def update(self):
        param_pool = self.env['ir.config_parameter']
        ur1 = "https://www.sotersat.com/api/v1.0/devlist"
        api_key = str(param_pool.get_param("res.config.settings.api_key"))
        if not api_key:
            return {
                            'type': 'ir.actions.act_window',
                            'name': 'LogIn',
                            'res_model': 'sotersat.login.wizard',
                            'view_mode': 'form',
                            'target': 'new'
                        }
        headers = {'Content-type': 'application/json','X-Sotersat-Api-Key': api_key}
        r = requests.get(ur1, data=json.dumps({}), headers=headers)
        data = json.loads(r.text)
        vehicle_pool = self.env['fleet.vehicle']
        odoo_meter_pool = self.env['fleet.vehicle.odometer']
        if data.get(u'ResponseCode',0)==200:
            for device in data.get(u'deviceList',[]):
                dev_assign_veh = vehicle_pool.search([('gps_device_id','=',device.get(u'deviceId',False))])
                
                for item in dev_assign_veh:
                    odoo_rec = odoo_meter_pool.create({
                                                        'vehicle_id': item.id,
                                                        'value': device.get('odometer'),
                                                        'date': datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                                                        'current_device_id': device.get('deviceId')
                                                        })
                    item.write({
                                   'last_update_date_time': datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                                    'odometer_id': odoo_rec.id
                                    })
            return {
                'type': 'ir.actions.act_window',
                'name': 'Success..',
                'res_model': 'odometer.update.sucess',
                'view_mode': 'form',
                'target': 'new'
            }
        elif data.get(u'additionalInfo','') and data.get(u'Status',''):
                    raise Warning(_('Can not update Odometer reading for all vehicles \n Error : %s' % data.get(u'additionalInfo','')))
        else:
            return {
                            'type': 'ir.actions.act_window',
                            'name': 'LogIn',
                            'res_model': 'sotersat.login.wizard',
                            'view_mode': 'form',
                            'target': 'new'
                        }
#             raise Warning(_('Can not update Odometer reading for all vehicles'))
        return True
        
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: