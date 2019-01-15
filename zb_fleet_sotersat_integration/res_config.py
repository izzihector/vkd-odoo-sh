# -*- coding: utf-8 -*-

import json,requests
from odoo import api, fields, models
from odoo import tools, _
from odoo.exceptions import Warning
from odoo.tools.safe_eval import safe_eval
from odoo.tools import ustr




class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    
    account = fields.Char(string="Account")
    user_name = fields.Char(string="User")
    password = fields.Char(string="Password")
    api_key = fields.Char(string="API Key")
    
    
        
    @api.model
    def get_default_alias_domain(self, fields):
        alias_domain = self.env["ir.config_parameter"].get_param("mail.catchall.domain", default=None)
        if alias_domain is None:
            domain = self.env["ir.config_parameter"].get_param("web.base.url")
            try:
                alias_domain = urlparse.urlsplit(domain).netloc.split(':')[0]
            except Exception:
                pass
        return {'alias_domain': alias_domain or False}

        
    @api.multi
    def set_default_api_key(self):
        for record in self:
            if record.api_key:
                self.env['ir.config_parameter'].set_param("res.config.settings.api_key", str(record.api_key) or '')
     
#     @api.model 
#     def get_default_api_key(self,fields):
#         
#         
#         print ('>>>>>>>>>>>>>>>',api_key)
#         return {'api_key': api_key and str(api_key) or False}
    
    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        api_key = self.env["ir.config_parameter"].get_param("res.config.settings.api_key", default=None)
        res.update(api_key=api_key)
        return res
        
    @api.multi
    def write_api_key(self,api_key):
        config_parameters = self.env['ir.config_parameter']
        for record in self:
            config_parameters.set_param("res.config.settings.api_key", api_key and str(api_key) or '')
            config_parameters.set_param("res.config.settings.account", '' )
            config_parameters.set_param("res.config.settings.user_name", '' )
            config_parameters.set_param("res.config.settings.password", '' )
#             
    @api.multi        
    def get_apit_key(self):
        config_parameters = self.env['ir.config_parameter']
        for rec in self:
            account = rec.account
            user = rec.user_name
            password = rec.password
            headers = {'Content-type': 'application/json'}
            data = {"account":account,
                    "userName":user,
                    "password":password}
            url = "https://www.sotersat.com/api/v1.0/authenticate"
            r = requests.post(url, data=json.dumps(data), headers=headers)
            authenitcated_data = json.loads(r.text)
            if authenitcated_data.get('ResponseCode','') == 200:
                api_key = authenitcated_data.get('apiKey','')
                self.write_api_key(api_key=api_key)
                rec.write({'api_key': api_key,'account': '','user_name': '','password': '',})
            else:
                raise Warning(_('Connection Failed....Please check the credentials'))
#             
    def remove_case_sensitive_num_plate(self,checking_objs, req_val):
        final_list = []
        for item in checking_objs:
            if item.license_plate.upper() == req_val.upper():
                final_list.append(item.id)
        return final_list
#             
    def checking_with_licence_plate(self,device,vehicle_pool):
        allocated_vehicles = vehicle_pool.search([('license_plate','=ilike',device.get(u'licensePlate'))])
        allocated_vehicles = vehicle_pool.browse(self.remove_case_sensitive_num_plate(allocated_vehicles, device.get(u'licensePlate')))
        if allocated_vehicles.ids:
            if len(allocated_vehicles) > 1:
                raise Warning(_('There is more than one vehicle with License Plate : %s ' % device.get('licensePlate')))
            else:
                for allocated_vehicle in allocated_vehicles:
                    if allocated_vehicle.gps_device_id and allocated_vehicle.gps_device_id != device.get(u'deviceId',False):
                        raise Warning(_('Data inconsistency : Vehicle %s have Wrong SOTERSAT Account ID Licence combination' % allocated_vehicle.name_get()[0][1]))
                    else:
                        allocated_vehicle.gps_device_id = device.get(u'deviceId',False)
                        vehicle_obj = allocated_vehicle
        else:
            vehicle_obj = self.create_vechilces(vehicle_pool,device)
        return vehicle_obj
#                         
    def checking_with_soter_account(self,device,vehicle_pool):
        allocated_vehicles = vehicle_pool.search([('gps_device_id','=',device.get(u'deviceId'))])
        if allocated_vehicles.ids:
            if len(allocated_vehicles) > 1:
                raise Warning(_('Data Inconsistency : There is more than one vehicle with SOTERSAT Account ID : %s ' % device.get(u'deviceId',False)))
            else:
                for allocated_vehicle in allocated_vehicles:
                    if allocated_vehicle.license_plate and allocated_vehicle.license_plate != device.get(u'licensePlate',False):
                        vechicle_name = allocated_vehicle.name_get()[0][1]
                        raise Warning(_('Data inconsistency : Sotersat ID must be unique, do not populate another vehicle with same ID’s, Please check Vehicle %s ' % (str(vechicle_name))))
                    else:
                        allocated_vehicle.license_plate = device.get(u'licensePlate',False)
                        vehicle_obj = allocated_vehicle
        else:
            vehicle_obj = self.create_vechilces(vehicle_pool,device)
        return vehicle_obj
#         
#                         
    def create_vechilces(self,vehicle_pool,device):
        brand_id = model_obj = brand_obj = model_id = False
        model_pool = self.env['fleet.vehicle.model']
        brand_pool = self.env['fleet.vehicle.model.brand']
        new_vehicle = False
        if device.get(u'model',False) and device.get(u'brand',False):
            model_obj = model_pool.search([('name','=',device.get(u'model'))]) and\
                            model_pool.search([('name','=',device.get(u'model'))])[0] or False
            brand_obj = brand_pool.search([('name','=',device.get(u'brand'))]) and \
                        brand_pool.search([('name','=',device.get(u'brand'))])[0] or False
            if brand_obj:
                brand_id = brand_obj.id
            if model_obj:
                model_id = model_obj.id
            if not model_id:
                if not brand_id:
                    brand_id = brand_pool.create({'name': device.get(u'brand')}).id
                model_id = model_pool.create({'name': device.get(u'model'),'brand_id': brand_id}).id
         
        if model_id:
            new_vehicle = vehicle_pool.create({
                                 'license_plate':device.get(u'licensePlate',False),
                                 'gps_device_id': device.get(u'deviceId',False),
                                 'model_id': model_id,
#                                  'hr_driver_id': driver_id
                                 })
        return new_vehicle
#             
    def assign_driver(self,device,vehicle_obj):
        driver_id = False
        hr_pool = self.env['hr.employee']
        if device.get(u'driverId'):
            driver_ids = hr_pool.search([('emp_id','=',ustr(device.get(u'driverId')))])
            if len(driver_ids) > 1:
                raise Warning(_('There is more than one driver with driver id  %s' % device.get(u'driverId','')))
            elif len(driver_ids) == 1:
                vehicle_obj.hr_driver_id = driver_ids[0].id
                 
#             
    def create_driver(self,headers):
        driver_url = "https://www.sotersat.com/api/v1.0/driverlist"
        driver_res = requests.get(driver_url, data=json.dumps({}), headers=headers)
        driver_data = json.loads(driver_res.text)
        if driver_data.get(u'ResponseCode',0) == 401:
            return {
                            'type': 'ir.actions.act_window',
                            'name': 'LogIn',
                            'res_model': 'sotersat.login.wizard',
                            'view_mode': 'form',
                            'target': 'new'
                        }
         
        if driver_data.get(u'ResponseCode',0) == 200:
            hr_pool = self.env['hr.employee']
            for driver in driver_data.get(u'driverList',[]):
                driver_exist = hr_pool.search([('emp_id','=',driver.get(u'driverID'))])
                if not driver_exist:
                    hr_pool.create({
                                   'mobile_phone': driver.get(u'MobileNumber'),
                                   'name': driver.get(u'FirstName','') + ' ' +driver.get(u'LastName',''),
                                   'rfid': driver.get(u'RFID',''),
                                   'emp_id': driver.get(u'driverID',''),
                                   })
             
    @api.multi
    def get_update_sotersat(self):
        for rec in self:
            param_pool = self.env['ir.config_parameter']
            ur1 = "https://www.sotersat.com/api/v1.0/devlist"
            api_key = str(param_pool.get_param("res.config.settings.api_key"))
            headers = {'Content-type': 'application/json','X-Sotersat-Api-Key': api_key}
            self.create_driver(headers)
            r = requests.get(ur1, data=json.dumps({}), headers=headers)
            data = json.loads(r.text)
            vehicle_pool = self.env['fleet.vehicle']
            odoo_meter_pool = self.env['fleet.vehicle.odometer']
            if data.get(u'ResponseCode',0)==200:
                for device in data.get(u'deviceList',[]):
                    if device.get(u'licensePlate',False):
                        vehicle_obj = self.checking_with_licence_plate(device,vehicle_pool)
                    if device.get(u'deviceId',False):
                        vehicle_obj = self.checking_with_soter_account(device, vehicle_pool)
                    if vehicle_obj:
                        self.assign_driver(device,vehicle_obj)
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
#                 raise Warning(_('Please check credentials'))
            return {
                            'type': 'ir.actions.act_window',
                            'name': 'Success..',
                            'res_model': 'conditino.check.sucess',
                            'view_mode': 'form',
                            'target': 'new'
                        }
            
            
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:    