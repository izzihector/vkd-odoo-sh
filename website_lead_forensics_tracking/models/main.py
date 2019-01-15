from odoo import fields, models

class TrakingCode(models.Model):
	_name = 'website'
	_inherit = "website"

	lead_forensics_tracking_code = fields.Char(string='Lead Forensics Tracking Code', size=255)
