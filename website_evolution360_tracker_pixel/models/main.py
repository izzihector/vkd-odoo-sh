from odoo import fields, models

class TrakingCode(models.Model):
	_name = 'website'
	_inherit = "website"

	evolution360_tracker_pixel = fields.Char(string='Evolution360 tracker Pixel', size=255)
