from openerp import api, fields, models, exceptions, tools,_
from openerp.exceptions import UserError, ValidationError

class ArtsBlogpost(models.Model):
	_name = 'website'
	_inherit = "website"

	logo_image = fields.Binary(string='Logo')
	icon_image = fields.Binary(string='Icon')
