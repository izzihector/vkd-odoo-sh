from odoo import fields, models

class TrakingCode(models.Model):
	_name = 'website'
	_inherit = "website"

	facebook_pixel = fields.Char(string='Facebook Pixel Code', size=255)
