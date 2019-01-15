# See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api


class OocMessageModel(models.Model):
    _name = 'ooc.message.model'
    _description = "Odoo Outlook Connector Message Model"

    name = fields.Char(string="Display Name", required=True, translate=True, help="This is the name of the model that the user will see in Outlook")
    model_id = fields.Many2one('ir.model', string='Model', required=True)
    model = fields.Char(related='model_id.model', store=True)

    @api.model
    def get_allowed_models(self):
        sr_models = self.search_read()
        allowed_models = []

        for sr_m in sr_models:
            try:
                self.env[sr_m['model']].check_access_rights('read')

                allowed_models.append({'name': sr_m['name'], 'model': sr_m['model']})
            except:
                pass

        return allowed_models

    @api.model
    def get_allowed_items(self, params):
        fields = ['id', 'display_name', 'name']
        is_project = False
        domain = [('name', 'ilike', params['search'])]

        if params['model'] == 'project.project':
            fields.append('privacy_visibility')
            fields.append('message_is_follower')
            is_project = True

        if len(self.env['ir.model.fields'].search([('model', '=', params['model']), ('name', '=', 'display_name'), ('store', '=', True)])):
            domain = [('display_name', 'ilike', params['search'])]

        sr_items = self.env[params['model']].search_read(domain, fields, limit=10)
        allowed_items = []

        for sr_i in sr_items:
            if is_project:
                # if sr_i['privacy_visibility'] != 'employees':
                if not sr_i['message_is_follower']:
                    continue

                del sr_i['privacy_visibility']
                del sr_i['message_is_follower']

            allowed_items.append(sr_i)

        return allowed_items
