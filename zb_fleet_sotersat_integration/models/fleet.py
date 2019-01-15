# -*- coding: utf-8 -*-

import json,requests
from odoo import api, fields, models
from odoo import tools, _
from odoo.exceptions import Warning
from datetime import date, datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.safe_eval import safe_eval

class fleet_vehicle(models.Model):
    _inherit = 'fleet.vehicle'
    
    @api.depends('gps_device_id')
    def _get_vehicle_url(self):
        for rec in self:
            param_pool = self.env['ir.config_parameter']
            api_key = str(param_pool.get_param("res.config.settings.api_key"))
            if api_key and rec.gps_device_id:
                self.vehicle_url_fn = 'https://www.sotersat.com/webapp/odoo/%s/%s' % (api_key,rec.gps_device_id)
    
    gps_device_id = fields.Char(string="SOTERSAT Device ID",track_visibility='onchange')
    last_update_date_time = fields.Datetime(string='Last Update Time') 
    imei = fields.Char(string="IMEI #",track_visibility='onchange')
    hr_driver_id = fields.Many2one('hr.employee',string="Driver")
    vehicle_url_fn = fields.Char(string="Vehicle Url",compute='_get_vehicle_url')
        
    @api.multi
    def refresh_button(self):
        param_pool = self.env['ir.config_parameter']
        headers = {'Content-type': 'application/json'}
        api_key = str(param_pool.get_param("res.config.settings.api_key"))
        if not api_key:
            return {
                            'type': 'ir.actions.act_window',
                            'name': 'LogIn',
                            'res_model': 'sotersat.login.wizard',
                            'view_mode': 'form',
                            'target': 'new'
                        }
        vehicle_pool = self.env['fleet.vehicle']
        odoo_meter_pool = self.env['fleet.vehicle.odometer']
#         if authenitcated_data.get('ResponseCode','')==200:
        for vehicle in self:
#             api_key = authenitcated_data.get('apiKey','')
            if vehicle.gps_device_id:
                device_url = "https://www.sotersat.com/api/v1.0/odometer/%s" % (vehicle.gps_device_id,)
                headers = {'Content-type': 'application/json','X-Sotersat-Api-Key': api_key}
                r = requests.get(device_url, data={}, headers=headers)
                data = json.loads(r.text)
                if data.get(u'ResponseCode',0)==200:
                    device_details = data.get(u'deviceList',[])
                    if device_details:
                        for div in device_details:
                            vehicle_objs = vehicle_pool.search([('gps_device_id','=',div.get('deviceId'))])
                            for vehicle in vehicle_objs:
                                odoo_rec = odoo_meter_pool.create({
                                                        'vehicle_id': vehicle.id,
                                                        'value': div.get('odometer'),
                                                        'date': datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                                                        'current_device_id': div.get('deviceId')
                                                        })
                                vehicle.write({
                                               'last_update_date_time': datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                                                'odometer_id': odoo_rec.id
                                                })
                        return {
                            'type': 'ir.actions.act_window',
                            'name': 'Updated..',
                            'res_model': 'odometer.refresh',
                            'view_mode': 'form',
                            'target': 'new'
                        }
                    else:
                        raise Warning(_('Can not update the Odometer, There is no device with divice id %s' % (vehicle.gps_device_id,)))
                elif data.get(u'additionalInfo','') and data.get(u'Status',''):
                    raise Warning(_('Error : %s' % data.get(u'additionalInfo','')))
                else:
                    return {
                            'type': 'ir.actions.act_window',
                            'name': 'LogIn',
                            'res_model': 'sotersat.login.wizard',
                            'view_mode': 'form',
                            'target': 'new'
                        }
#                     raise Warning(_('Can not update the Odometer, Please correctly configure Sotersat from Settings --> General Settings'))
            else:
                raise Warning(_('Can not update the Odometer, Please Assign a SOTERSAT Account ID'))
#     else:
#         raise Warning(_('Please correctly configure Sotersat from Settings --> General Settings'))
            
class fleet_vehicle_odometer(models.Model):
    _inherit = 'fleet.vehicle.odometer'
    
    date =  fields.Datetime(string='Date',default=fields.Date.today)
    current_device_id = fields.Char(string="Device Id")
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:                    
            