# -*- coding: utf-8 -*-
import json,requests
from odoo import api, fields, models
from odoo.exceptions import Warning
from odoo.tools import ustr
from odoo import tools, _

class update_trip_wizard(models.TransientModel):
    """update_trip_wizard"""
    _name = "update.trip.wizard"
    
    operation = fields.Selection([
            ('current_day','Update current day Trips'),
            ('selected_vehicle','Update selected vehicle Trips '),
            ('all_vehilces','Update All vehicles  Trips '),
        ], string='Select')
    vehicle_id = fields.Many2one('fleet.vehicle',string="Vehicle")
    
    @api.multi
    def update_trips(self):
        for wiz in self:
            if not wiz.operation:
                raise Warning(_(' Please select one option...'))
            updating_vehilces = False
            vehicle_pool = self.env['fleet.vehicle']
            trip_pool = self.env['sotersat.trip.details']
            param_pool = self.env['ir.config_parameter']
            api_key = str(param_pool.get_param("res.config.settings.api_key"))
            if not api_key:
                return {
                            'type': 'ir.actions.act_window',
                            'name': 'LogIn',
                            'res_model': 'sotersat.login.wizard',
                            'view_mode': 'form',
                            'target': 'new'
                        }
            if wiz.operation=='selected_vehicle':
                if not wiz.vehicle_id: 
                    raise Warning(_('Please select any vehicle...'))
                updating_vehilces = [wiz.vehicle_id]
                
            elif wiz.operation=='all_vehilces':
                updating_vehilces = vehicle_pool.search([('gps_device_id','!=','null')])
            if not api_key:
                raise Warning(_('Error in api key, Please correctly configure Sotersat from Settings --> General Settings'))
            if api_key and updating_vehilces and wiz.operation in ['selected_vehicle','all_vehilces']:
                for vehicle in updating_vehilces:
                    if vehicle.gps_device_id:
                        
                        url = 'https://www.sotersat.com/api/v1.0/trips/%s/fromId/0' % vehicle.gps_device_id
                        headers = {'Content-type': 'application/json','X-Sotersat-Api-Key': api_key}
                        r = requests.get(url, data={}, headers=headers)
                        data = json.loads(r.text)
                        if data.get(u'ResponseCode',0) == 200:
                            trips = data.get(u'trips',[])
                            vehicle_pool = self.env['fleet.vehicle']
                            for trip in trips:
                                trip_data = {
                                             'stop_lon': trip.get(u'StopLon',0) and float(trip.get(u'StopLon',0)),
                                             'stop_addr':  trip.get(u'StopAddress',False) and ustr(trip.get(u'StopAddress','')),
                                             'stop_lat': trip.get(u'StopLat','') and float(trip.get(u'StopLat','')),
                                            'dist': trip.get(u'distance',0),
                                            'driver': trip.get(u'Driver',0) and ustr(trip.get(u'Driver',0)),
                                            'private': trip.get(u'Private',0) and int(trip.get(u'Private',0)),
                                            'start_lat': trip.get(u'StartLat',0) and float(trip.get(u'StartLat',0)),
                                            'note': trip.get(u'Note','') and ustr(trip.get(u'Note','')),
                                             'duration': trip.get(u'duration',0) and ustr(trip.get(u'duration',0)),
                                             'stop_time': trip.get(u'StopTime',False) and str(trip.get(u'StopTime',False)),
                                            'stop_odometer': trip.get(u'StopOdometer',0) and float(trip.get(u'StopOdometer',0)),
                                            'start_odometer': trip.get(u'StartOdometer',0) and float(trip.get(u'StartOdometer',0)),
                                            'start_time': trip.get(u'StartTime',False) and ustr(trip.get(u'StartTime',False)),
                                            'start_addr': trip.get(u'StartAddress','') and ustr(trip.get(u'StartAddress','')),
                                            'start_long': trip.get(u'StartLon',0) and float(trip.get(u'StartLon',0)),
                                            'trip_id': trip.get(u'Id',0) and int(trip.get(u'Id',0)),
                                            'device_id': trip.get(u'deviceID',0) and int(trip.get(u'deviceID',0)),
                                             
                                             }
                                if trip.get(u'additionalInformation'):
                                    add_info=trip.get(u'additionalInformation')
                                    trip_data.update({'engine_idle':add_info.get(u'engineIdle',False) and ustr(add_info.get(u'engineIdle',False)),
                                                      'toll':add_info.get(u'toll',False) and ustr(add_info.get(u'toll',False)),
                                                      'maxspeed':add_info.get(u'maxspeed',0) and int(add_info.get(u'maxspeed',0)),
                                                      'oneway':add_info.get(u'oneway','') and ustr(add_info.get(u'oneway',''))
                                                      
                                                      })
                                check_exist = trip_pool.search([('trip_id','=',trip_data.get('trip_id'))])
                                if not check_exist:
                                    related_vehicle_id = vehicle_pool.search([('gps_device_id','=',trip_data.get('device_id',False))]) and vehicle_pool.search([('gps_device_id','=',trip_data.get('device_id',False))])[0].id
                                    trip_data.update({'vehicle_id': related_vehicle_id})
                                    if related_vehicle_id:
                                        trip_pool.create(trip_data)
                        elif data.get(u'additionalInfo','') and data.get(u'Status',''):
                            raise Warning(_('Error : %s' % data.get(u'additionalInfo','')))
                        elif data.get(u'ResponseCode',0)==401:
                            raise Warning(_('Error : Please Check %s' % vehicle.name_get()[0][1]))
                        else:
                            
                            return {
                            'type': 'ir.actions.act_window',
                            'name': 'LogIn',
                            'res_model': 'sotersat.login.wizard',
                            'view_mode': 'form',
                            'target': 'new'
                        }
#                             raise Warning(_('Can not update, Please correctly configure Sotersat from Settings --> General Settings'))
                        
                        
                        
                        
                    else:
                        raise Warning(_('Error : There is no device id for %s' % vehicle.name_get()[0][1] ))
            elif wiz.operation == 'current_day':
                trip_pool.update_trip()
                
            else:
                raise Warning(_('Error : Updation failed %s'  ))
                
                
                    
    
    
        
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: