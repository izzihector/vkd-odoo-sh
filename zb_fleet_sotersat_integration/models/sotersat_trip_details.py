# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models
from odoo import tools, _
import json,requests
from odoo.tools import ustr

class sotersat_trip_details(models.Model):
    _name = 'sotersat.trip.details'
    
    _rec_name ='vehicle_id'
    _order = 'start_time desc'
    
    @api.depends('trip_id')
    def _get_trip_vehicle_url(self):
        for rec in self:
            param_pool = self.env['ir.config_parameter']
            api_key = str(param_pool.get_param("res.config.settings.api_key"))
            if api_key and rec.trip_id:
                self.vehicle_trip_url_fn = 'https://www.sotersat.com/webapp/odoo/showtrips/%s/%s' % (api_key,rec.trip_id)
    
    stop_lon =  fields.Float(string='Stop Longitude')
    stop_addr =  fields.Char(string='Stop Address')
    stop_lat = fields.Float(string='Stop Latitude')
    dist =  fields.Float(string='Distance')
    driver = fields.Char(string='Driver')
    private = fields.Integer(string='Private') 
    start_lat = fields.Float(string='Start Latitude')
    note = fields.Text(string='Note')
    duration = fields.Char(string='Duration')
    stop_time = fields.Datetime(string='StopTime')
    stop_odometer = fields.Float(string='Stop Odometer')
    start_odometer = fields.Float(string='Start Odometer')
    start_time = fields.Datetime(string='Start Time')
    start_addr = fields.Char(string='Start Address')
    start_long = fields.Float(string='Start Longitude')
    trip_id = fields.Integer(string='Trip Id')
    device_id = fields.Integer(string='deviceID')
    vehicle_id = fields.Many2one('fleet.vehicle',string="Vehicle")
    vehicle_trip_url_fn = fields.Char(string="Vehicle Url",compute='_get_trip_vehicle_url')
    engine_idle = fields.Boolean(string="Engine Idle")
    toll = fields.Boolean(string="Toll")
    maxspeed = fields.Integer(string="Max Speed")
    oneway = fields.Selection([('yes','Yes'),('no','No')],string="One Way")
    
    
    @api.model
    def update_trip(self):
        param_pool = self.env['ir.config_parameter']
        api_key = str(param_pool.get_param("res.config.settings.api_key"))
        if api_key:
            url = 'https://www.sotersat.com/api/v1.0/trips' 
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
                    check_exist = self.search([('trip_id','=',trip_data.get('trip_id'))])
                    if not check_exist:
                        related_vehicle_id = vehicle_pool.search([('gps_device_id','=',trip_data.get('device_id',False))]) and vehicle_pool.search([('gps_device_id','=',trip_data.get('device_id',False))])[0].id
                        trip_data.update({'vehicle_id': related_vehicle_id})
                        if related_vehicle_id:
                            self.create(trip_data)
            elif data.get(u'ResponseCode',0) == 401:
                return {
                            'type': 'ir.actions.act_window',
                            'name': 'LogIn',
                            'res_model': 'sotersat.login.wizard',
                            'view_mode': 'form',
                            'target': 'new'
                        }
        else:
            return {
                            'type': 'ir.actions.act_window',
                            'name': 'LogIn',
                            'res_model': 'sotersat.login.wizard',
                            'view_mode': 'form',
                            'target': 'new'
                        }
                    
                     

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: