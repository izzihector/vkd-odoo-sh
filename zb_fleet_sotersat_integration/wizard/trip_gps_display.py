# -*- coding: utf-8 -*-
from odoo import api, fields, models

class trip_gps_dipsplay(models.TransientModel):
    """trip gps display"""
    _name = "trip.gps.display"
    
    @api.model
    def _get_default_gps(self):
        param_pool = self.env['ir.config_parameter']
        trip_pool = self.env['sotersat.trip.details']
        api_key = str(param_pool.get_param("res.config.settings.api_key"))
        url = ''
        if api_key and self._context.get('active_ids',[]):
            url = 'https://www.sotersat.com/webapp/odoo/showtrips/%s' % (api_key)
            for trip_id in  self._context.get('active_ids',[]):
                sotersat_trip_id = trip_pool.browse(trip_id).trip_id
                if sotersat_trip_id:
                    url += '/'
                    url += str(sotersat_trip_id)
        return url
    gps_vehicle = fields.Char(string="Vehicle",default=_get_default_gps)
    
        
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: