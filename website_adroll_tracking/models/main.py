from odoo import fields, models

class AdrollTag(models.Model):
	_name = 'website'
	_inherit = "website"

	adroll_adv_id = fields.Char(string='Adroll Adv Id', size=255)
	adroll_pix_id = fields.Char(string='Adroll Pix Id', size=255)
